##############
# Moderation.py
##############

from commons import Error
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
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=Error.user_missing_permission("Manage Messages"))
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=Error.invalid_command_usage(self.bot, "purge [amount] (max 100)"))

def setup(bot):
    bot.add_cog(Moderation(bot))