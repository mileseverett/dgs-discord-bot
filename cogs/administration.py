import os
import random
import pickle
import string
import json

import discord
from discord.ext import commands

from utils import jsonHandling

class adminSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    def whitelistCheck(self,ctx):
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        print(settings)
        print(ctx.message.channel.id)
        if ctx.message.channel.id in settings["whitelistedChannels"]:
            return True
        else:
            return False

    @commands.command(name="whitelistchannel")
    @commands.has_any_role("Admin",":)")
    async def whitelistChannel(self,ctx):
        try:
            fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"

            if os.path.exists(fname):
                settings = jsonHandling.loadJSON(fname)
            else: 
                settings = {}

            if "whitelistedChannels" in settings.keys():
                settings["whitelistedChannels"].append(ctx.message.channel.id)
            else:
                settings["whitelistedChannels"] = []
                settings["whitelistedChannels"].append(ctx.message.channel.id)
            
            print(settings)
            
            jsonHandling.dumpJSON(fname,settings)
            await ctx.send("Channel added to the whitelist.")
        except Exception as e:
            print(e)
            
    @commands.command(name="removewhitelistchannel")
    @commands.has_any_role("Admin",":)")
    async def removeWhitelistChannel(self,ctx):
        try:
            fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
            print(fname)
            if os.path.exists(fname):
                settings = jsonHandling.loadJSON(fname)
            else: 
                settings = {}
        
            #check if any channels have ever been whitelisted
            if "whitelistedChannels" in settings.keys():
                #try to remove the channel this message was sent from
                try:
                    settings["whitelistedChannels"].remove(ctx.message.channel.id)
                
                #will throw an error if doesn't exist, so tell user it wasn't ever whitelisted.
                except Exception as e:
                    await ctx.send("This channel wasn't whitelisted.")
            #tell user that no channels have ever been whitelisted in this server
            else:
                await ctx.send("No channels have ever been whitelisted in this server.")

            print(settings)
            print("fname again",fname)
            jsonHandling.dumpJSON(fname,settings)
            await ctx.send("Channel removed from the whitelist.")
        except Exception as e:
            print(e)

    @commands.command(name="channelcheck")
    @commands.has_any_role("Admin",":)")
    async def channelCheck(self,ctx):
        if self.whitelistCheck(ctx) == True:
            await ctx.send("Channel is whitelisted")
        else:
            await ctx.send("Channel is not whitelisted")


    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')

def setup(bot):
    bot.add_cog(adminSystem(bot))