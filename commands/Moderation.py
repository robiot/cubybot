##############
# Moderation.py
##############

from re import purge
from discord.ext.commands.errors import CheckFailure
from Errors import Errors as _error
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Purge
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, count: int):        
        count = max(1, min(count, 100))
        await ctx.message.channel.purge(limit=count, bulk=True)
        await ctx.send(f'Removed **{count}** messages.', delete_after=5)
    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=_error.default_error("You don't have permission to use this command."))
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=_error.invalid_command_usage(self.bot, "purge [amount] (max 100)"))

def setup(bot):
    bot.add_cog(Moderation(bot))