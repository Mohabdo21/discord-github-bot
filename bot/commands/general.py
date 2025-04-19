import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="hello", description="Say hello to the bot")
    async def hello(self, ctx: commands.Context) -> None:
        """Say hello to the bot."""
        embed = discord.Embed(
            title="Hello!",
            description=f"How can I assist you today, {ctx.author.mention}?",
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="commands", description="Show help message"
    )  # Changed from 'help'
    async def commands_list(self, ctx: commands.Context) -> None:
        """Show help message."""
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are the available commands:",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="General",
            value="`hello` - Say hello\n`commands` - Show this message",
            inline=False,
        )

        embed.add_field(name="Fun", value="`roll` - Roll a dice", inline=False)

        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
