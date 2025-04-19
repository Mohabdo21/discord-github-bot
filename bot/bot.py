import hashlib
import hmac
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="?",
            intents=intents,
            activity=discord.Game(name="Type ?help"),
            case_insensitive=True,
        )
        self.web_app = FastAPI()
        self.setup_webhook_routes()

    async def setup_hook(self) -> None:
        """Load extensions on startup."""
        await self.load_extension("bot.commands.general")
        await self.load_extension("bot.commands.fun")
        # Add more extensions here

    def verify_signature(self, signature: str, payload: bytes) -> bool:
        secret = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()
        if not secret:
            return True  # Skip verification if no secret set

        expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def send_github_notification(self, channel_id: int, payload: dict):
        try:
            channel = self.get_channel(channel_id)
            if not channel:
                print(f"Channel {channel_id} not found")
                return

            event_type = payload.get(
                "X-GitHub-Event", "push"
            )  # Default to push if not specified
            repo = payload["repository"]
            sender = payload["sender"]

            # Base embed setup
            embed = discord.Embed(color=0x28A745)
            embed.set_author(name=sender["login"], icon_url=sender["avatar_url"])
            embed.set_footer(
                text=repo["full_name"],
                icon_url="https://github.githubassets.com/favicons/favicon.png",
            )

            if event_type == "push":
                await self._handle_push_event(embed, payload, repo)
            elif event_type == "pull_request":
                await self._handle_pull_request(embed, payload, repo)
            # Add more event types as needed

            await channel.send(embed=embed)

        except Exception as e:
            print(f"Error sending notification: {e}")
            # Consider sending a basic error notification to Discord
            if channel:
                await channel.send(f"⚠️ Failed to process GitHub webhook: {str(e)}")

    async def _handle_push_event(self, embed: discord.Embed, payload: dict, repo: dict):
        """Handle GitHub push events with detailed information."""
        commits = payload["commits"]
        branch = payload["ref"].split("/")[-1]
        compare_url = payload["compare"]

        # Main embed details
        embed.title = f"📌 {len(commits)} new commit{'s' if len(commits) > 1 else ''} to {repo['name']}"
        embed.url = compare_url
        embed.description = f"Branch: **{branch}**\n[View changes]({compare_url})"

        # Add repository stats if available
        if repo.get("stargazers_count") is not None:
            embed.add_field(
                name="Repository Stats",
                value=f"⭐ {repo['stargazers_count']} | 🍴 {repo['forks_count']}",
                inline=True,
            )

        # Show first 3 commits (Discord limits embeds)
        for commit in commits[:3]:
            short_sha = commit["id"][:7]
            commit_time = commit["timestamp"].split("T")[0]  # Just the date

            embed.add_field(
                name=f"{short_sha}: {commit['message'][:50]}{'...' if len(commit['message']) > 50 else ''}",
                value=f"By {commit['author']['name']} on {commit_time}\n[View]({commit['url']})",
                inline=False,
            )

        if len(commits) > 3:
            embed.add_field(
                name="More commits",
                value=f"+{len(commits) - 3} additional commits not shown",
                inline=False,
            )

        # Add language/topic badges if available
        if repo.get("language"):
            embed.add_field(name="Language", value=repo["language"], inline=True)

        if repo.get("topics"):
            embed.add_field(
                name="Topics",
                value=", ".join([f"`{topic}`" for topic in repo["topics"][:3]]),
                inline=True,
            )

    async def _handle_pull_request(
        self, embed: discord.Embed, payload: dict, repo: dict
    ):
        """Handle GitHub pull request events."""
        pr = payload["pull_request"]
        action = payload["action"]  # opened, closed, merged, etc.

        # Set color based on PR state
        color_map = {
            "opened": 0x2CBE4E,  # Green
            "closed": 0xCB2431,  # Red
            "merged": 0x6F42C1,  # Purple
        }
        embed.color = color_map.get(action, 0x28A745)

        embed.title = f"🔀 PR #{pr['number']}: {pr['title']} ({action})"
        embed.url = pr["html_url"]
        embed.description = pr["body"][:200] + ("..." if len(pr["body"]) > 200 else "")

        # Add PR metadata
        embed.add_field(
            name="Status",
            value=f"`{pr['state']}` → `{pr['merged'] and 'merged' or pr['mergeable_state']}`",
            inline=True,
        )

        embed.add_field(
            name="Changes",
            value=f"➕ {pr['additions']} | ➖ {pr['deletions']} | 📄 {pr['changed_files']}",
            inline=True,
        )

        if pr["requested_reviewers"]:
            reviewers = ", ".join([r["login"] for r in pr["requested_reviewers"]])
            embed.add_field(name="Reviewers", value=reviewers, inline=False)

    def setup_webhook_routes(self):
        @self.web_app.post("/github-webhook")
        async def github_webhook(request: Request):
            try:
                payload_bytes = await request.body()
                signature = request.headers.get("X-Hub-Signature-256", "")

                if not self.verify_signature(signature, payload_bytes):
                    raise HTTPException(status_code=401, detail="Invalid signature")

                payload = await request.json()
                channel_id = int(os.getenv("GITHUB_NOTIFICATION_CHANNEL"))

                self.loop.create_task(
                    self.send_github_notification(channel_id, payload)
                )

                return {"status": "success"}

            except Exception as e:
                print(f"Webhook error: {e}")
                raise HTTPException(status_code=400, detail=str(e))

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle command errors globally."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Use `?help` for available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
        else:
            logging.error(f"Error in command {ctx.command}: {error}")
            await ctx.send("An error occurred while executing that command.")
