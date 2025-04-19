import asyncio
import logging
import os
import threading
from typing import Optional

import discord
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global Discord client for webhooks
_discord_client: Optional[discord.Client] = None
_client_ready = threading.Event()


def get_discord_client() -> discord.Client:
    """
    Get or create a shared Discord client instance.

    Returns:
        discord.Client: A connected Discord client instance
    """
    global _discord_client, _client_ready

    if _discord_client is None:
        # Create a minimal client just for sending messages
        intents = discord.Intents.default()
        intents.message_content = True
        _discord_client = discord.Client(intents=intents)

        # Set up the ready event
        @_discord_client.event
        async def on_ready():
            logger.info(
                f"Shared Discord client logged in as {_discord_client.user} (ID: {_discord_client.user.id})"
            )
            _client_ready.set()

        # Start the client in a separate thread
        token = os.getenv("TOKEN")
        if not token:
            raise ValueError("Discord TOKEN not found in environment variables")

        def run_client_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_discord_client.start(token))

        client_thread = threading.Thread(target=run_client_thread, daemon=True)
        client_thread.start()

        # Wait for client to be ready (with timeout)
        if not _client_ready.wait(timeout=30):
            logger.warning("Discord client initialization timed out")

    return _discord_client


def send_notification(channel_id: int, embed: discord.Embed) -> bool:
    """
    Send a notification to a Discord channel.

    Args:
        channel_id: The ID of the channel to send to
        embed: The embed to send

    Returns:
        bool: True if sent successfully, False otherwise
    """
    client = get_discord_client()

    async def send_message():
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel {channel_id} not found")
                return False

            await channel.send(embed=embed)
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    try:
        # Case 1: When running in an existing event loop (e.g., FastAPI context)
        if asyncio.get_running_loop():
            # Schedule the task in the existing loop
            future = asyncio.run_coroutine_threadsafe(send_message(), client.loop)
            return future.result(timeout=10)  # Wait max 10 seconds
    except RuntimeError:
        # Case 2: When no event loop is running (standalone context)
        try:
            return asyncio.run(send_message())
        except RuntimeError as e:
            logger.error(f"Failed to run send_message: {e}")
            return False
