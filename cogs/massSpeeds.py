import math
import random
import numpy as np
from pprint import pprint

import discord
from discord.ext import commands

class massSpeeds(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    def printTeams(self, ctx, finalTeams, leftoverList):
        for k,v in finalTeams.items():
            print(k, "is:", v)
        print("Leftovers for this round are:", ', '.join(leftoverList))
        return 1

    @commands.command(name="runRandomMassSpeeds") # you can change this name Miles
    @commands.has_any_role("Reviewer", "Admin") # more roles? probably always have a reviewer/admin I guess?
    async def runRandomMassSpeeds(self, ctx, participants):
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

        for k,v in sorted(participants.items(), key=lambda item: item[1], reverse = True):
            maskTeam = [0] * numTeams
            for i in range(len(finalTeams)):
                if len(list(finalTeams.values())[i]) == 5:
                    maskTeam[i] = 1
            indexNum = np.ma.array(teamWeight, mask = maskTeam).argmin() # find team with lowest weight that does NOT already have 5 people
            finalTeams['Team ' + str(indexNum + 1)].append(str(k))
            teamWeight[indexNum] = teamWeight[indexNum] + v

        printTeams(finalTeams, leftoverList)
        return finalTeams, leftoverList
        
def setup(bot):
    bot.add_cog(massSpeeds(bot))