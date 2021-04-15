import sys
import traceback
import discord
from discord.ext import commands

class otherSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="source")
    async def source(self, ctx):
        """
        Callable Function for returning the source code for the bot
        """
        await ctx.send("Source is: https://github.com/mileseverett/dgs-discord-bot")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')
    
def setup(bot):
    bot.add_cog(otherSystem(bot))