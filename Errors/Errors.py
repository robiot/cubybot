##############
# Errors.py
##############

import discord
from discord.ext import commands

def invalid_command_usage(bot, text):
    embed = discord.Embed(description=f"Invalid command usage, try using it like:\n`{bot.command_prefix+text}`", color=discord.Color.red())
    return embed

def default_error(text):
    embed = discord.Embed(description=text, color=discord.Color.red())
    return embed