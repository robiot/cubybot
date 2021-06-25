from always_active import keep_alive
from discord.ext import commands
import discord
import dotenv
import os

version = "0.0.2-open-beta"

#Only run keep_alive if ran on replit
if [k for k in os.environ.keys() if 'REPL_' in k] != []:
  keep_alive()

dotenv.load_dotenv()
intents = discord.Intents.default()  
intents.members = True 
bot = commands.Bot(command_prefix=";", intents=intents)

for file in os.listdir("./commands"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"commands.{name}")

@bot.command()
async def about(ctx):
    embed = discord.Embed(title=f"Created by robiot#5485", color=discord.Color.green())
    embed.add_field(name="About", value=f"{len(bot.guilds)} servers\n\n[Bot Invite](https://discord.com/api/oauth2/authorize?client_id=851876864279838770&permissions=8&scope=bot)")

    embed.set_footer(text=f"{bot.user.name} Version {version}")
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name=f"{bot.command_prefix}help", url="https://www.twitch.tv/sus"))
    print(f'Online as {bot.user}!')

bot.run(os.getenv('TOKEN'))