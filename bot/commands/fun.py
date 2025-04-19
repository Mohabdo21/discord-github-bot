import random

import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="roll", description="Roll a dice")
    async def roll(self, ctx: commands.Context) -> None:
        """Roll a dice."""
        result = random.randint(1, 6)
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a **{result}**!",
            color=discord.Color.random(),
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="howareyou", description="Ask how the bot is doing")
    async def how_are_you(self, ctx: commands.Context) -> None:
        """Ask how the bot is doing."""
        responses = [
            "I'm just a bot, but I'm functioning well!",
            "01010100 01101000 01100001 01101110 01101011 01110011 00100000 01100110 01101111 01110010 01100001 01110011 01101011 01101001 01101110 01100111 00100001",  # "Thanks for asking!" in binary
            "I'm great! How about you?",
            "All systems operational!",
            "I'm just a bunch of code, but my mood is always 100%!",
        ]
        await ctx.send(random.choice(responses))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
