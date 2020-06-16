import os
import random
import pickle
import string
import json

import discord
from discord.ext import commands

class vouchSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot



    def dumpPickle(self,fname,data):
        with open(fname, 'w') as filehandle:
            json.dump(data, filehandle)
        return 

    def loadPickle(self,fname):
        with open(fname, 'r') as filehandle:
            data = json.load(filehandle)
            print (data)
        return data

    def attemptVouch(self,name,amount,vouches,flipModifier):
        print ("attempting to vouch")
        print ("amount:",amount,"flipmodifier",flipModifier)
        if name in vouches.keys():
            vouches[name]["vouches"] = max(vouches[name]["vouches"] + amount + flipModifier,0)
        else:
            print ("no vouches")
            vouches[name] = {"vouches":max(amount + flipModifier,0),"vouchers":{},"antivouchers":{}}   
        print ("vouch successful")    
        return vouches

    def vouchValue(self,roles):
        value = 0
        if "Floorgazer" in roles:
            value = 3
        elif "Keyer" in roles:
            value = 2
        elif "Wingman" in roles or "Wingwoman" in roles:
            value = 1
        return value

    def getRoles(self,ctx):
        roles = []
        for x in ctx.author.roles:
            roles.append(x.name)
        return roles

    def argvCombiner(self,argv):
        newString = ""
        for x in argv:
            newString = newString + x + " "
        return newString

    def whitelistCheck(self,ctx):
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = self.loadPickle(fname)
        print (settings)
        print (ctx.message.channel.id)
        if ctx.message.channel.id in settings["whitelistedChannels"]:
            return True
        else:
            return False

    @commands.command(name="vouch")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman")
    async def vouch(self, ctx, user:str, *argv):
        user = user.lower()
        antiModifier = 0
        vouchReason = self.argvCombiner(argv)
        try:
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"

            if os.path.exists(fname):
                vouches = self.loadPickle(fname)
            else: 
                vouches = {}

            roles = self.getRoles(ctx)
            print (roles)
            rankValue = self.vouchValue(roles)

            try: 
                prevValue = vouches[user]["vouchers"][ctx.author.name]["value"]
            except:
                prevValue = 1000

            try:  
                if ctx.author.name in vouches[user]["vouchers"] and rankValue == vouches[user]["vouchers"][ctx.author.name]["value"]:
                    await ctx.send("Already vouched at current rank value.")
                    return
            except Exception as e:
                print (e)
                pass
            try:
                if ctx.author.name in vouches[user]["antivouchers"]:
                    antiModifier = vouches[user]["antivouchers"][ctx.author.name]["value"]
            except: 
                pass

            authorName = ctx.author.name

            try:
                #check if vouch is an update or not
                print (rankValue,prevValue)
                if ctx.author.name in vouches[user]["vouchers"] and rankValue > prevValue:
                    print ("update vouch")
                    newRankValue = rankValue - vouches[user]["vouchers"][ctx.author.name]["value"]
                    vouches = self.attemptVouch(user,newRankValue,vouches,antiModifier)
                    vouchType = "Vouch update"
                else:
                    print ("new vouch")
                    vouches = self.attemptVouch(user,rankValue,vouches,antiModifier)
                    vouchType = "Vouch"
            #case where vouches is empty
            except:
                vouches = self.attemptVouch(user,rankValue,vouches,antiModifier)
                vouchType = "Vouch"

            try:
                del vouches[user]["antivouchers"][authorName]
            except:
                pass

            vouches[user]["vouchers"][authorName] = {
                "value":rankValue,
                "reason":vouchReason[:-1]
            }


            self.dumpPickle(fname,vouches)

            print ("vouch complete:",vouches)
            await ctx.send(vouchType + " " + string.capwords(user) + ". They are now on " + str(vouches[user]["vouches"]))
        except Exception as e:
            print (e)

    @commands.command(name="antivouch")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman")
    async def antivouch(self, ctx, user:str,*argv):
        user = user.lower()
        antiModifier = 0

        vouchReason = self.argvCombiner(argv)

        try:
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            if os.path.exists(fname):
                vouches = self.loadPickle(fname)
            else: 
                vouches = {}
            print ("loaded vouches",vouches)

            roles = self.getRoles(ctx)
            rankValue = self.vouchValue(roles)
            try:
                print ("rankValue",rankValue,"previousVouch",vouches[user]["antivouchers"][ctx.author.name]["value"])
            except Exception as e:
                print (e)
                pass
            try:
                if ctx.author.name in vouches[user]["antivouchers"] and rankValue == vouches[user]["antivouchers"][ctx.author.name]["value"]:
                    await ctx.send("Already antivouched at current rank value.")
                    return
            except:
                pass

            #checks if this user previously vouched them
            try:
                if ctx.author.name in vouches[user]["vouchers"]:
                    antiModifier = vouches[user]["vouchers"][ctx.author.name]["value"] * -1
            except: 
                pass
            
            authorName = ctx.author.name
            

            #updating antivouch
            if ctx.author.name in vouches[user]["antivouchers"] and rankValue > vouches[user]["antivouchers"][ctx.author.name]["value"]:
                newRankValue = rankValue - vouches[user]["antivouchers"][ctx.author.name]["value"]
                vouches = self.attemptVouch(user,newRankValue*-1,vouches,antiModifier)
                antivouchType = "Antivouch update"
            #if user hasn't antivouched before
            else:
                vouches = self.attemptVouch(user,rankValue*-1,vouches,antiModifier)
                antivouchType = "Antivouch"
            
            
            
            try:
                del vouches[user]["vouchers"][authorName]
            except:
                pass

            vouches[user]["antivouchers"][authorName] = {
                "value":rankValue,
                "reason":vouchReason[:-1]
            }

            #check if user has been vouched to 0 and remove if so
            if vouches[user]["vouches"] == 0:
                del vouches[user]
                await ctx.send("Reached 0 vouches. Removed " + user)

            self.dumpPickle(fname,vouches)
            print ("antivouch complete:",vouches)
            await ctx.send(antivouchType + " " + string.capwords(user) + ". They are now on " + str(vouches[user]["vouches"]))
        except Exception as e:
            print (e)

    @commands.command(name="vouchinfo")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman","3s","2s","1s")
    async def vouchInfo(self, ctx, user:str):

        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
        if os.path.exists(fname):
            vouches = self.loadPickle(fname)
        else: 
            await ctx.send("No vouches have been made on this server yet.")
        
        user = user.lower()
        roles = self.getRoles(ctx)
        try:
            embedTitle = "Vouches for " + string.capwords(user)
            embed=discord.Embed(title=embedTitle)

            vouchDict = {
                1:"<:wingman:722167334688784434>",
                2:"<:keyer:722167334357303368>",
                3:"<:floorgazer:722167334667550741>"
            }

            embed.add_field(name="Vouches", value=vouches[user]["vouches"], inline=False)
            
            try:
                #check if channel has been whitelisted
                if self.whitelistCheck(ctx) == False:
                    pass
                else:
                    #create text string with vouchers info
                    vouchers = ""
                    for k,v in vouches[user]["vouchers"].items():
                        vouchers = vouchers + vouchDict[v["value"]] + " " + k 
                        if len(v["reason"]) > 0:
                            vouchers = vouchers + " - " + str(v["reason"]) + "\n"
                        else:
                            vouchers = vouchers + "\n"
                    embed.add_field(name="Vouchers", value=vouchers, inline=False)

                    #if there is antivouchers
                    if len(vouches[user]["antivouchers"]) > 0:
                        antivouchers = ""
                        #create text string with antivouchers info
                        for k,v in vouches[user]["antivouchers"].items():
                            antivouchers = antivouchers + vouchDict[v["value"]] + " " + k
                            if len(v["reason"]) > 0:
                                vouchers = vouchers + " - " + str(v["reason"]) + "\n"
                            else:
                                vouchers = vouchers + "\n"
                    else:
                        antivouchers = "None"
                    embed.add_field(name="Antivouchers", value=antivouchers, inline=False)
            except:
                pass
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(e)
            await ctx.send("User does not exist")

    @commands.command(name="findall")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman")
    async def findAll(self,ctx):
        for x in ctx.guild.members:      
            roles = []
            print (type(x))
            roles.append(x.name)
            # for y in range(len(x)):
            #     roles.append(x[y].name)
            # await ctx.send(x.name,roles)
            # if "Floorgazer" in x.name.roles:
            #     await ctx.send(x.name,"Floorgazer")
            # elif "Keyer" in x.name.roles:
            #     await ctx.send(x.name,"Keyer")
            # elif "Wingman" in x.name.roles:
            #     await ctx.send(x.name,"Wingman")
            # else: 
            #     await ctx.send("Who's this guy!")
            

    @commands.command(name='create-channel')
    @commands.has_role('Admin')
    async def create_channel(self,ctx, channel_name="hello"):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            print(f'Creating a new channel: {channel_name}')
            await guild.create_text_channel(channel_name)

    @commands.command(name="count")
    async def count(self,ctx, number:int):
        for x in range(number):
            await ctx.send(x)

    @commands.command(name="contextinfo")
    async def contextInfo(self,ctx):
        await ctx.send(ctx.message)

    @commands.command(name="whitelistchannel")
    @commands.has_any_role("Admin",":)")
    async def whitelistChannel(self,ctx):
        try:
            fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"

            if os.path.exists(fname):
                settings = self.loadPickle(fname)
            else: 
                settings = {}

            if "whitelistedChannels" in settings.keys():
                settings["whitelistedChannels"].append(ctx.message.channel.id)
            else:
                settings["whitelistedChannels"] = []
                settings["whitelistedChannels"].append(ctx.message.channel.id)
            
            print (settings)
            
            self.dumpPickle(fname,settings)
            await ctx.send("Channel added to the whitelist.")
        except Exception as e:
            print (e)
            
    @commands.command(name="removewhitelistchannel")
    @commands.has_any_role("Admin",":)")
    async def removeWhitelistChannel(self,ctx):
        try:
            fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"

            if os.path.exists(fname):
                settings = self.loadPickle(fname)
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

            print (settings)
            
            self.dumpPickle(fname,settings)
            await ctx.send("Channel removed from the whitelist.")
        except Exception as e:
            print (e)

    @commands.command(name="channelcheck")
    @commands.has_any_role("Admin",":)")
    async def channelCheck(self,ctx):
        if self.whitelistCheck(ctx) == True:
            await ctx.send("Channel is whitelisted")
        else:
            await ctx.send("Channel is not whitelisted")

    @commands.command(name="addbuffer")
    @commands.has_any_role("Admin",":)")
    async def addBuffer(self,ctx,data):
        print ("adding to buffer")
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        print (fname)
        if os.path.exists(fname):
            settings = self.loadPickle(fname)
        else: 
            settings = {}
        print (settings)
        try: 
            vouchID = settings["vouchIDcounter"]
            settings["vouchIDcounter"] = settings["vouchIDcounter"] + 1
        except Exception as e:
            print (e)
            vouchID = 1
            settings["vouchIDcounter"] = vouchID + 1
        print (settings)
        self.dumpPickle(fname,settings)
        print (vouchID)
        buffername = "buffers/" + ctx.guild.name.replace(" ","") +   ".json"    
        print (buffername)
        if os.path.exists(buffername):
            testBuffer = self.loadPickle(buffername)
        else: 
            testBuffer = {}    
        print (testBuffer)
        testBuffer[vouchID] = data
        print (testBuffer)
        self.dumpPickle(buffername,testBuffer)
        
        await ctx.send("All done buddy")

    @commands.command(name="viewbuffer")
    @commands.has_any_role("Admin",":)")
    async def viewBuffer(self,ctx):
        
        buffername = "buffers/" + ctx.guild.name.replace(" ","") +  ".json"    
        print (buffername)
        if os.path.exists(buffername):
            testBuffer = self.loadPickle(buffername)
        else: 
            testBuffer = {}    
        print (testBuffer)
        embedTitle = "Bfs birthday"
        embed=discord.Embed(title=embedTitle)
        for k,v in testBuffer.items():
            embed.add_field(name=k, value=v, inline=False)   

        await ctx.send(embed=embed)

    @commands.command(name="removebuffer")
    @commands.has_any_role("Admin",":)")
    async def removeBuffer(self,ctx,bufferNo):
        
        buffername = "buffers/" + ctx.guild.name.replace(" ","") +  ".json"    
        print (buffername)
        if os.path.exists(buffername):
            testBuffer = self.loadPickle(buffername)
        else: 
            testBuffer = {}    
        
        del testBuffer[bufferNo]

        self.dumpPickle(buffername,testBuffer)
        await ctx.send("Removed from buffer.")    

    @commands.command(name="acceptbuffer")
    @commands.has_any_role("Admin",":)")
    async def acceptBuffer(self,ctx):
        try:
            buffername = "buffers/" + ctx.guild.name.replace(" ","") +  ".json"    
            print (buffername)
            if os.path.exists(buffername):
                testBuffer = self.loadPickle(buffername)
            else: 
                testBuffer = {}    

            for x in list(testBuffer):
                message = "Deleting ",x,testBuffer[x]
                await ctx.send(message)
                del testBuffer[x]
                print (testBuffer)

            self.dumpPickle(buffername,testBuffer)
            await ctx.send("Cleared buffer")
        except Exception as e:
            print (e)

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')

def setup(bot):
    bot.add_cog(vouchSystem(bot))