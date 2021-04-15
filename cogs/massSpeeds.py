import math
import random
import numpy as np
import os
import discord
from discord.ext import commands
from discord.utils import get

from utilities.misc import getRoles, createFolder
from utilities import jsonHandling

class massSpeeds(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.messageID = 0000000000000
        self.message = None
        self.teamMessages = []
        self.client = discord.Client()

        self.prodDGSBotID = 722758078310776832
        self.testDGSBotID = 718483095262855280

        createFolder("massSpeeds")

    def printTeams(self, finalTeams, leftoverList):
        """
        Helper function to print the created teams

        Parameters:
        finalTeams - Dictionary of the form {"Team": "Participant"}
        leftoverList - List of leftover players
        """
        for k,v in finalTeams.items():
            print(k, "is:", v)
        print("Leftovers for this round are:", ', '.join(leftoverList))
        return 1

    def rankValue(self, roles):
        """
        Helper function to define DGS rank values

        Parameters:
        roles - list of roles, currently populated from getRoles()
        """
        value = 0
        if "Floorgazer" in roles:
            value = 7
        elif "Keyer" in roles:
            value = 5
        elif "Wingman" in roles or "Wingwoman" in roles:
            value = 3
        elif "3S" in roles:
            value = 2
        elif "2S" in roles:
            value = 1
        elif "1S" in roles:
            value = 1
        else: 
            # anyone missing a role is assumed to be 1S
            value = 1
        return value

    def runRandomMassSpeeds(self, participants):
        """
        Main helper function to create and output teams

        Parameters:
        participants - is a dictionary of the form {"RSN":"Rank"}
            - "RSN" is the discord name
            - "Rank" is a number from rankValue corresponding to their weighting in the randomizing algorithm
        """
        
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

        # print the teams to the console
        self.printTeams(finalTeams, leftoverList)
        return finalTeams, leftoverList

    def joinMassSpeeds(self, guild, member):
        """
        Adds member to the list of active participants. Triggered by reacting to the emote in the bot message

        Parameters:
        Member - Discord ID for the user who reacted
        """
        MSfname = "massSpeeds/" + guild.name.replace(" ","") + ".json"
        players = jsonHandling.loadJSON(MSfname)
        players[str(member.id)] = 0
        jsonHandling.dumpJSON(MSfname, players)

    def leaveMassSpeeds(self, guild, member):
        """
        Remove member from the list of active participants. Triggered by removing reaction to the emote in the bot message

        Parameters:
        Member - Discord ID for the user who reacted
        """
        # remove participant from the JSON file
        MSfname = "massSpeeds/" + guild.name.replace(" ","") + ".json"
        players = jsonHandling.loadJSON(MSfname)
        players.pop(str(member.id))
        jsonHandling.dumpJSON(MSfname, players)

    @commands.command(name="msstart")
    @commands.has_any_role("Mass Speeds Admin")
    async def startMassSpeedsSession(self, ctx):
        """
        Callable function to begin a mass speeds session. Initializes the participant list and creates a reactable message

        """
        usersMessage = ctx.message
        await usersMessage.delete()
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        if "msActive" in settings.keys():
            if settings["msActive"] == False:
                message = await ctx.send("React to this message to join the mass speeds session.")
                self.messageID = message
                self.message = message
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
    async def endMassSpeedsSession(self, ctx):
        """
        Callable function to end the current session. Clears the participant list

        """
        fname = "guildsettings/" + ctx.guild.name.replace(" ", "") + ".json"
        settings = jsonHandling.loadJSON(fname)
        if "msActive" in settings.keys():
            if settings["msActive"] == True:
                await self.message.delete()
                settings["msActive"] = False
            elif settings["msActive"] == False:
                await ctx.send("MS was not running.")
        else:
            settings["msActive"] = False

        MSfname = "massSpeeds/" + ctx.guild.name.replace(" ", "") + ".json"
        players = jsonHandling.loadJSON(MSfname)
        jsonHandling.dumpJSON(MSfname, {})

        jsonHandling.dumpJSON(fname, settings)
        for x in players.keys():
            member = ctx.guild.get_member(int(x))
            role = get(ctx.guild.roles, name="Mass Speeds")
            if role in member.roles: 
                await member.remove_roles(role)

        if len(self.teamMessages) > 0:
            for x in range(len(self.teamMessages)):
                msg = self.teamMessages.pop()
                await msg.delete()
        
    @commands.command("msteams")
    @commands.has_any_role("Mass Speeds Admin")
    async def formTeams(self, ctx):
        """
        Callable function to creates teams based on active participants, rank values and then outputs those teams into the server

        """
        usersMessage = ctx.message
        await usersMessage.delete()
        MSfname = "massSpeeds/" + ctx.guild.name.replace(" ", "") + ".json"
        fname = "guildsettings/" + ctx.guild.name.replace(" ", "") + ".json"
        settings = jsonHandling.loadJSON(fname)
        if "msActive" not in settings.keys():
            await ctx.send("No mass speeds session in progress. <a:EB:744967488751665303> (Not in settings)")
            return

        if settings["msActive"] == False:
            await ctx.send("No mass speeds session in progress. <a:EB:744967488751665303> (MS Session = False)")
            return     

        if len(self.teamMessages) > 0:
            for x in range(len(self.teamMessages)):
                msg = self.teamMessages.pop()
                await msg.delete()

        players = jsonHandling.loadJSON(MSfname)
        MSrole = get(ctx.guild.roles, name="Mass Speeds")

        playersValue = {}
        toBeRemoved = []
        for x in players.keys():
            member = ctx.guild.get_member(int(x))
            if MSrole in member.roles:
                value = self.rankValue(getRoles(member.roles))
                if member.nick == None:
                    playersValue[member.name] = value
                else:
                    playersValue[member.nick] = value
            else:
                toBeRemoved.append(x)

        for x in toBeRemoved:
            players.pop(str(x))

        jsonHandling.dumpJSON(MSfname,players)
        teams, leftovers = self.runRandomMassSpeeds(playersValue)

        for k,v in teams.items():
            team = discord.Embed()
            message = ""
            for x in v:
                message = message + x + "\n"
            
            team.add_field(name=k, value=message, inline=False)
            messageSent = await ctx.send(embed=team)
            self.teamMessages.append(messageSent)
        
        message = ""
        if len(leftovers) > 0:
            for x in leftovers:
                message = message + x + "\n"
        else:
            message = "None"
        leftovers = discord.Embed()
        leftovers.add_field(name="Leftovers", value=message)
        messageSent = await ctx.send(embed=leftovers)
        self.teamMessages.append(messageSent)

    @commands.command("msreset")
    @commands.has_any_role("Mass Speeds Admin")
    async def resetMassSpeeds(self, ctx):
        """
        Callable function to reset the Mass Speeds Session

        """
        fname = "guildsettings/" + ctx.guild.name.replace(" ", "") + ".json"
        settings = jsonHandling.loadJSON(fname)
        settings["msActive"] = False
        jsonHandling.dumpJSON(fname, settings)

        MSfname = "massSpeeds/" + ctx.guild.name.replace(" ", "") + ".json"
        jsonHandling.dumpJSON(MSfname,{})

    @commands.command("msforcecheck")
    @commands.has_any_role("Mass Speeds Admin")
    async def forceCheckRole(self, ctx):
        """
        Checking function. Lists all users who have the role and in JSON

        """
        usersMessage = ctx.message
        await usersMessage.delete()
        MSfname = "massSpeeds/" + ctx.guild.name.replace(" ","") + ".json"
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        if "msActive" not in settings.keys():
            await ctx.send("No mass speeds session in progress. <a:EB:744967488751665303> (Not in settings)")
            return

        if settings["msActive"] == False:
            await ctx.send("No mass speeds session in progress. <a:EB:744967488751665303> (MS Session = False)")
            return

        players = {}

        MSrole = get(ctx.guild.roles, name="Mass Speeds")
        
        for x in ctx.guild.members:
            if MSrole in x.roles and x.id != self.prodDGSBotID and x.id != self.testDGSBotID:
                players[x.id] = 0

        jsonHandling.dumpJSON(MSfname, players)
        await ctx.send(players)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Remove a member from the Mass Speeds list

        """
        print (type(self.messageID))
        print ("messageID",self.messageID)
        print ("messageID.id",self.messageID.id)
        print ("message_id",payload.message_id)
        if self.messageID.id == payload.message_id and payload.emoji.name == "EB" and payload.user_id != self.prodDGSBotID and payload.user_id != self.testDGSBotID:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = get(guild.roles, name="Mass Speeds")
            if role not in member.roles:
                await member.add_roles(role)
                self.joinMassSpeeds(guild, member)
            
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """
        Adds a member to the Mass Speeds list

        """
        print (type(self.messageID))
        print ("messageID",self.messageID)
        print ("messageID.id",self.messageID.id)
        print ("message_id",payload.message_id)
        if self.messageID.id == payload.message_id and payload.emoji.name == "EB" and payload.user_id != self.prodDGSBotID and payload.user_id != self.testDGSBotID:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = get(guild.roles, name="Mass Speeds")
            if role in member.roles: 
                await member.remove_roles(role)
                self.leaveMassSpeeds(guild, member)
            
def setup(bot):
    bot.add_cog(massSpeeds(bot))