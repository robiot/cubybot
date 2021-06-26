##############
# Utility.py
##############

from Errors import Errors as error
from gtts import gTTS as gtts
from discord.ext import commands
from os import remove
import discord
import asyncio

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def serverinfo(self, ctx):
        embed = discord.Embed(title=ctx.guild.name, color=discord.Color.blue())
        embed.add_field(name="Owner", value=ctx.guild.owner)
        embed.add_field(name="Region", value=ctx.guild.region)
        embed.add_field(name="Channel Categories", value=len(ctx.guild.categories))
        embed.add_field(name="Text Channels", value=len(ctx.guild.text_channels))
        embed.add_field(name="Voice Channels", value=len(ctx.guild.voice_channels))
        embed.add_field(name="Members", value=ctx.guild.member_count)

        embed.set_footer(text=f"ID: {ctx.guild.id} | Server Created ~ {ctx.guild.created_at.strftime('%Y-%m-%d')}")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member=None):
        if member is None: member = ctx.message.author
        embed = discord.Embed(title=member.name, color=discord.Color.blue())
        embed.add_field(name="Joined", value=member.joined_at.strftime('%Y-%m-%d'))
        embed.add_field(name="Registered", value=member.created_at.strftime('%Y-%m-%d'))
        embed.set_footer(text=f"ID: {member.id}")
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! Latency is {round(self.bot.latency * 10000)}ms')

    @commands.command()
    async def poll(self, ctx, *, text=None):
        if text == None: await ctx.send(embed=error.invalid_command_usage(self.bot, "poll [text]")); return
        embed = discord.Embed(title=text, color=discord.Color.teal())
        poll = await ctx.send(embed=embed)
        await poll.add_reaction('✅')
        await poll.add_reaction('❌')

    @commands.command()
    async def members(self, ctx):
        embed = discord.Embed(title="Members", description=ctx.guild.member_count, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command()
    async def tts(self, ctx, *, text=None):
        if not text or len(text) >= 100: return await ctx.send(embed=error.invalid_command_usage(self.bot, "tts [text] (max 100 chars)"))
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.send(embed=error.default_error('You have to be in a voice channel to use this command.'))
        
        vc = ctx.voice_client
        if vc:
            try:
                await vc.move_to(voice_channel)
            except asyncio.TimeoutError:
                return await ctx.send(embed=error.voice_timeout_error(f'Moving to channel: <{voice_channel.name}> timed out'))
        else:
            vc = await voice_channel.connect()
        
        gtts(text=f"{ctx.author.display_name} said {text}", lang="en", slow=False).save(f"./temp/{ctx.message.guild.id}.mp3")
        
        try:
            vc.play(discord.FFmpegPCMAudio(f'./temp/{ctx.message.guild.id}.mp3'), after=print("Done"))
            embed = discord.Embed(title="", description=f"Talking in : {voice_channel.name}", color=discord.Color.green())
            await ctx.send(embed=embed)    
        except discord.errors.ClientException:
            return await ctx.send(embed=error.default_error("Already playing audio"))
        await asyncio.sleep(0.6)
        remove(f"./temp/{ctx.message.guild.id}.mp3")

def setup(bot):
    bot.add_cog(Utility(bot))