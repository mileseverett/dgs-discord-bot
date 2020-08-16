import os
import random
import pickle
import string
import json
import requests
import sys
import traceback
import urllib.request
import discord
from discord.ext import commands

from utils import jsonHandling

class otherSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vis")
    async def vis(self, ctx):
        try:
            url = "http://www.runeguide.info/alt1/viswax/api/getVisWaxCombo.php"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            # await ctx.send(data)
            runes = jsonHandling.loadJSON("realrunes.json")
            # await ctx.send(runes)
            for k,v in data.items():
                embedTitle = "VIS WAX YO"
                embed=discord.Embed(title=embedTitle)
                s1 = data[k]["slot1_best"] 
                s1other= data[k]["slot1_other"]
                s21 = data[k]["slot2_1_best"] 
                s21other= data[k]["slot2_1_other"]
                s22 = data[k]["slot2_2_best"] 
                s22other= data[k]["slot2_2_other"]
                s23 = data[k]["slot2_3_best"] 
                s23other= data[k]["slot2_3_other"]
                if s1other:
                    s1test = ""
                    for x in s1other:
                        s1test = s1test + " " +  runes[x["id"]] + " " + x["vis"] + "\n"
                else:
                    s1test = "None"
                if len(s21other[0]) > 0:
                    s21test = ""
                    for x in s21other:
                        s21test = s21test + " " +  runes[x["id"]] + " " + x["vis"] + "\n"
                else:
                    s21test = "None"
                if len(s22other[0]) > 0:
                    s22test = ""
                    for x in s22other:
                        s22test = s22test + " " +  runes[x["id"]] + " " + x["vis"] + "\n"
                else: 
                    s22test = "None"
                if len(s23other[0]) > 0:                
                    s23test = ""
                    for x in s23other:
                        s23test = s23test + " " +  runes[x["id"]] + " " + x["vis"] + "\n"
                else:
                    s23test = "None"
                embed.add_field(name="Last updated", value=data[k]["lastupdated_format"], inline=False)
                embed.add_field(name="Slot 1", value=runes[s1], inline=False)
                embed.add_field(name="Slot 1 alternatives", value=s1test, inline=False)
                embed.add_field(name="Slot 2-1", value=runes[s21], inline=False)
                embed.add_field(name="Slot 2-1 alternatives", value=s21test, inline=False)
                embed.add_field(name="Slot 2-2", value=runes[s22], inline=False)
                embed.add_field(name="Slot 2-2 alternatives", value=s22test, inline=False)
                embed.add_field(name="Slot 2-3", value=runes[s23], inline=False)
                embed.add_field(name="Slot 2-3 alternatives", value=s23test, inline=False)

                await ctx.send(embed=embed)
                break
            
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')
    
    @commands.command(name="source")
    async def source(self, ctx):
        print("Source is: " + "https://github.com/mileseverett/dgs-discord-bot")

def setup(bot):
    bot.add_cog(otherSystem(bot))