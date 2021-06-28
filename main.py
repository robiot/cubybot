from discord.errors import Forbidden
from always_active import keep_alive
from discord.ext import commands
from commons import Error
import discord
import dotenv
import os

version = "0.1.1-open-beta"

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

class CustomHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, color=discord.Colour.blurple())
            try: await destination.send(embed=emby)
            except Forbidden: await destination.send(Error.bot_missing_permission("Embed Links"))
bot.help_command = CustomHelp()

@bot.command()
async def about(ctx):
    embed = discord.Embed(title=f"Created by robiot#5485", color=discord.Color.green())
    embed.add_field(name="About", value=f"{len(bot.guilds)} servers\n\n[Bot Invite](https://discord.com/oauth2/authorize?client_id=851876864279838770&scope=bot&permissions=8589934591)")

    embed.set_footer(text=f"{bot.user.name} Version {version}")
    await ctx.send(embed=embed)

async def presence():
    await bot.change_presence(activity=discord.Streaming(name=f"{bot.command_prefix}help | {len(bot.guilds)} servers", url="https://www.twitch.tv/sus"))

@bot.event
async def on_ready():
  await presence()

@bot.event
async def on_guild_join(guild):
  await presence()

bot.run(os.getenv('TOKEN'))