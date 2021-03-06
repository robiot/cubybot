##############
# Fun.py
##############
from commons import Error
from discord.ext import commands
import discord
import aiohttp
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        embed = discord.Embed(title="", description="")
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/dankmemes/new.json?sort=hot') as r:
                res = await r.json()
                embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, question=None):
        if not question or len(question) < 3: return await ctx.send(embed=Error.invalid_command_usage(self.bot, "8ball [question] (min 3 chars)"))
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        await ctx.send(random.choice(responses))

    @commands.command()
    async def howgay(self, ctx, member: discord.Member=None):
        if member is None: member = ctx.message.author
        embed = discord.Embed(title="Howgay Calculator", description=f"{member.name} is {random.randint(0,100)}% gay 🏳️‍🌈")
        await ctx.send(embed=embed)

    @commands.command()
    async def pp(self, ctx, member: discord.Member=None):
        if member is None: member = ctx.message.author
        embed = discord.Embed(title="Peepe Size Calculator", description=f"{member.name}'s pp\n 8{''.join('=' for i in range(random.randint(0,20)))}D")
        await ctx.send(embed=embed)

    @commands.command()
    async def joke(self, ctx):
        async with aiohttp.request('GET', 'https://icanhazdadjoke.com', headers={'Accept': 'text/plain'}) as r:
            await ctx.send(await r.text())


def setup(bot):
    bot.add_cog(Fun(bot))