##############
# Error.py
##############

import discord
from discord.ext import commands

def invalid_command_usage(bot, text):
    embed = discord.Embed(description=f"Invalid command usage, try using it like:\n`{bot.command_prefix+text}`", color=discord.Color.red())
    return embed

def user_missing_permission(text):
    embed = discord.Embed(description=f"You don't have permission to use this command. Required permission [{text}]", color=discord.Color.red())
    return embed

def bot_missing_permission(text):
    return f"Im missing required permissions execute this command. Needed permission [{text}]"

def default_error(text):
    embed = discord.Embed(description=text, color=discord.Color.red())
    return embed