import math
import random
import numpy as np
from pprint import pprint

import discord
from discord.ext import commands
from discord.utils import get

from utils.misc import getRoles
from utils import jsonHandling

class massSpeeds(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.messageID = None
        self.client = discord.Client()

    def printTeams(self, finalTeams, leftoverList):
        for k,v in finalTeams.items():
            print(k, "is:", v)
        print("Leftovers for this round are:", ', '.join(leftoverList))
        return 1

    def rankValue(self, roles):
        value = 0
        if "Floorgazer" in roles:
            value = 9
        elif "Keyer" in roles:
            value = 7
        elif "Wingman" in roles or "Wingwoman" in roles:
            value = 5
        elif "3S" in roles:
            value = 4
        elif "2S" in roles:
            value = 2
        elif "1S" in roles:
            value = 1
        else: 
            value = 1
        return value



    def runRandomMassSpeeds(self, participants):
        # Assumes participants is a dictionary of the form {"RSN":"Rank"}
        # Where "Rank" is a number from 1 to 6
        # RSN is just what appears in the output
        
        numTeams = math.floor(len(participants)/5)
        numLeftover = len(participants) - (5*numTeams)

        # Prepare leftovers - if no leftovers then leave it null
        leftoverList = []
        if numLeftover != 0:
            for key in random.sample(participants.keys(), numLeftover):
                leftoverList.append(key)
                del participants[key]

        # Make list of dict's with length for number of teams to fill
        finalTeams = {}
        for i in range(numTeams):
            finalTeams.update({"Team " + str(i + 1): []})
        teamWeight = np.zeros(numTeams)

        for k,v in sorted(participants.items(), key=lambda item: (item[1], random.random()), reverse = True):
            maskTeam = [0] * numTeams
            for i in range(len(finalTeams)):
                if len(list(finalTeams.values())[i]) == 5:
                    maskTeam[i] = 1
            indexNum = np.ma.array(teamWeight, mask = maskTeam).argmin() # find team with lowest weight that does NOT already have 5 people
            finalTeams['Team ' + str(indexNum + 1)].append(str(k))
            teamWeight[indexNum] = teamWeight[indexNum] + v

        self.printTeams(finalTeams, leftoverList)
        return finalTeams, leftoverList


    @commands.command(name="msstart")
    @commands.has_any_role("Mass Speeds Admin")
    async def startMassSpeedsSession(self,ctx):
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        if "msActive" in settings.keys():
            if settings["msActive"] == False:
                message = await ctx.send("React to this dumdums")
                self.messageID = (message)
                await message.add_reaction("<a:EB:744967488751665303>")
                settings["msActive"] = True
            elif settings["msActive"] == True:
                await ctx.send("MS session already running!")
        else:
            settings["msActive"] = True

        MSfname = "massSpeeds/" + ctx.guild.name.replace(" ","") + ".json"
        jsonHandling.dumpJSON(MSfname,{})

        jsonHandling.dumpJSON(fname,settings)

    @commands.command(name="msend")
    @commands.has_any_role("Mass Speeds Admin")
    async def endMassSpeedsSession(self,ctx):
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        if "msActive" in settings.keys():
            if settings["msActive"] == True:
                await self.messageID.delete()
                settings["msActive"] = False
            elif settings["msActive"] == False:
                await ctx.send("MS was not running.")
        else:
            settings["msActive"] = False

        MSfname = "massSpeeds/" + ctx.guild.name.replace(" ","") + ".json"
        jsonHandling.dumpJSON(MSfname,{})

        jsonHandling.dumpJSON(fname,settings)
        


    def joinMassSpeeds(self,guild,member):
        MSfname = "massSpeeds/" + guild.name.replace(" ","") + ".json"
        players = jsonHandling.loadJSON(MSfname)
        players[str(member.id)] = 0
        jsonHandling.dumpJSON(MSfname,players)

    def leaveMassSpeeds(self,guild,member):    
        MSfname = "massSpeeds/" + guild.name.replace(" ","") + ".json"
        players = jsonHandling.loadJSON(MSfname)
        players.pop(str(member.id))
        jsonHandling.dumpJSON(MSfname,players)

    @commands.command("msteams")
    async def formTeams(self,ctx):
        MSfname = "massSpeeds/" + ctx.guild.name.replace(" ","") + ".json"
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        if "msActive" not in settings.keys():
            await ctx.send("No mass speeds session in progress. <a:EB:744967488751665303> (Not in settings)")
            return

        if settings["msActive"] == False:
            await ctx.send("No mass speeds session in progress. <a:EB:744967488751665303> (MS Session = False)")
            return     

        players = jsonHandling.loadJSON(MSfname)

        MSrole = get(ctx.guild.roles, name="Mass Speeds")

        playersValue = {}
        toBeRemoved = []

        for x in players.keys():
            member = ctx.guild.get_member(int(x))
            print (member.roles)
            if MSrole in member.roles:
                value = self.rankValue(getRoles(member.roles))
                playersValue[member.name] = value
            else:
                toBeRemoved.append(x)

        print (players)

        a, b = self.runRandomMassSpeeds(playersValue)
        await ctx.send(a)
        await ctx.send(b)

    @commands.command("ms")
    async def massSpeeds(self,ctx):
        MSfname = "massSpeeds/" + ctx.guild.name.replace(" ","") + ".json"
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        if "msActive" not in settings.keys():
            await ctx.send("No mass speeds session in progress. <a:EB:744967488751665303> (Not in settings)")
            return

        if settings["msActive"] == False:
            await ctx.send("No mass speeds session in progress. <a:EB:744967488751665303> (MS Session = False)")
            return

        players = jsonHandling.loadJSON(MSfname)
        playersText = ""
        for x in players.keys():
            playersText = playersText + x + "\n"

        await ctx.send(playersText)
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):

        if self.messageID.id == payload.message_id and payload.emoji.name == "EB" and payload.user_id != 722758078310776832:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = get(guild.roles, name="Mass Speeds")
            if role not in member.roles:
                await member.add_roles(role)
                self.joinMassSpeeds(guild,member)
            

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):

        if self.messageID.id == payload.message_id and payload.emoji.name == "EB" and payload.user_id != 722758078310776832:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = get(guild.roles, name="Mass Speeds")
            if role in member.roles: 
                await member.remove_roles(role)
                self.leaveMassSpeeds(guild,member)
            
def setup(bot):
    bot.add_cog(massSpeeds(bot))