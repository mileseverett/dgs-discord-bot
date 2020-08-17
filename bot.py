import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!',case_insensitive=True)

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        print ("loaded" + file)
        bot.load_extension(f'cogs.{file[:-3]}')        
         
bot.run(TOKEN)