import os
import random
import pickle
import string
import json
import sys, traceback
import datetime

import discord
from discord.ext import commands

from utils import jsonHandling, bufferHandling

class vouchSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.vouchDict = {
                1:"<:wingman:722167334688784434>",
                2:"<:keyer:722167334357303368>",
                3:"<:floorgazer:722167334667550741>"
            }

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
        else: 
            value = 0
        return value

    def getRoles(self,ctx):
        roles = []
        for x in ctx.author.roles:
            roles.append(x.name)
        return roles

    def checkHistory(self,vouchType,vouches,ctx,user):
        anti = 1
        if vouchType == "vouch":
            checkOppositeDict = "antivouchers"
            checkDict = "vouchers"
        elif vouchType == "antivouch":
            checkOppositeDict = "vouchers"
            checkDict = "antivouchers"
            anti = -1

        roles = self.getRoles(ctx)
        rankValue = self.vouchValue(roles)
        antiModifier = 0
        #check if this person has vouched/antivouched the user in the past and at what value
        try: 
            prevValue = vouches[user][checkDict][ctx.author.name]["value"]
        #set it to something high
        except:
            prevValue = 1000
            traceback.print_exc(file=sys.stdout)
        
        #check if this user has already vouched AND at the current value
        try:  
            if ctx.author.name in vouches[user][checkDict] and rankValue == prevValue:
                return False, {}
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)
            pass
        
        #check to see if this user is flipping their vouch/anti
        try:
            if ctx.author.name in vouches[user][checkOppositeDict]:
                antiModifier = vouches[user][checkOppositeDict][ctx.author.name]["value"] * -1
        except Exception as e:
            print (e) 
        print ("values",rankValue,prevValue)
        try:
            #check if vouch is an update or not
            if ctx.author.name in vouches[user][checkDict] and rankValue > prevValue:
                rankValue = rankValue - vouches[user][checkDict][ctx.author.name]["value"]             
        except Exception as ಠ_ಠ:
            print (ಠ_ಠ)
            traceback.print_exc(file=sys.stdout)

        vouchInfo = {
            "user":user,
            "rankValue":rankValue * anti,
            "antiModifier":antiModifier,
            "vouchType":vouchType
        }       

        return True, vouchInfo

    def argvCombiner(self,argv):
        newString = ""
        for x in argv:
            newString = newString + x + " "
        return newString

    def whitelistCheck(self,ctx):
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        print (settings)
        print (ctx.message.channel.id)
        if ctx.message.channel.id in settings["whitelistedChannels"]:
            return True
        else:
            return False

    @commands.command(name="vouch")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman")
    async def vouch(self, ctx, user:str, *argv):
        try:
            user = user.lower()
            vouchReason = self.argvCombiner(argv)
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            print (fname)
            vouches = jsonHandling.loadJSON(fname)
            acceptableVouch, vouchInfo = self.checkHistory("vouch",vouches,ctx,user)
            if acceptableVouch == False:
                await ctx.send("Unacceptable vouch.")
                return
            print (acceptableVouch,vouchInfo)
            authorName = ctx.author.name

            voucherInfo = {
                "value":vouchInfo["rankValue"],
                "reason":vouchReason[:-1],
                "voucher":authorName,
                "vouch queued":"find a way to store date/time"        
            }

            bufferData = {
                "vouchInfo":vouchInfo,
                "voucherInfo":voucherInfo
            }

            bufferHandling.addBuffer(ctx.guild.name.replace(" ",""),"vouches",bufferData)
            await ctx.send("Your vouch for " + user + " has been added to the queue to be reviewed by admins.")
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)
        
    @commands.command(name="antivouch")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman")
    async def antivouch(self, ctx, user:str,*argv):
        try:
            user = user.lower()
            vouchReason = self.argvCombiner(argv)
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            acceptableVouch, vouchInfo = self.checkHistory("antivouch",vouches,ctx,user)
            if acceptableVouch == False:
                await ctx.send("Unacceptable vouch.")
                return
            print (acceptableVouch,vouchInfo)
            authorName = ctx.author.name
            voucherInfo = {
                "value":vouchInfo["rankValue"],
                "reason":vouchReason[:-1],
                "voucher":authorName,
                "vouch queued":"find a way to store date/time"        
            }
            bufferData = {
                "vouchInfo":vouchInfo,
                "voucherInfo":voucherInfo
            }
            bufferHandling.addBuffer(ctx.guild.name.replace(" ",""),"vouches",bufferData)
            await ctx.send("Your vouch for " + user + " has been added to the queue to be reviewed by admins.")
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="vouchbuffer")
    async def viewVouchBuffer(self,ctx):
        try:
            bufferData = bufferHandling.getAllBufferData(ctx.guild.name.replace(" ",""),"vouches")
            print (bufferData)
            embed = discord.Embed(title="Vouches Buffer")
            for k,v in bufferData.items():
                vouchLine = string.capwords(v["vouchInfo"]["user"]) + " " + v["voucherInfo"]["voucher"]
                embed.add_field(name=k, value=vouchLine, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="removevouch")
    async def removeVouch(self,ctx,vouchID:str):
        try:   
            bufferHandling.removeBuffer(ctx.guild.name.replace(" ",""),"vouches",vouchID)
            await ctx.send("Removed from buffer.")  
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="acceptvouch")
    async def acceptVouch(self,ctx,vouchID:str):
        try:
            #get data for this vouchID
            vouchData = bufferHandling.getBufferData(ctx.guild.name.replace(" ",""),"vouches",vouchID)
            #get vouches data
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            #add the vouch to the vouch datastore
            vouches = self.attemptVouch(vouchData["vouchInfo"]["user"],vouchData["voucherInfo"]["value"],vouches,vouchData["vouchInfo"]["antiModifier"])          
           
            #add the voucher info to the vouch datastore
            #if it's a vouch
            if vouchData["vouchInfo"]["vouchType"] == "vouch":
                vouches[vouchData["vouchInfo"]["user"]]["vouchers"][vouchData["voucherInfo"]["voucher"]] = vouchData["voucherInfo"]
                try:
                    del vouches[vouchData["vouchInfo"]["user"]]["antivouchers"][vouchData["voucherInfo"]["voucher"]]
                except:
                    pass
            #if it's an antivouch
            elif vouchData["vouchInfo"]["vouchType"] == "antivouch":
                vouches[vouchData["vouchInfo"]["user"]]["antivouchers"][vouchData["voucherInfo"]["voucher"]] = vouchData["voucherInfo"]
                try:
                    del vouches[vouchData["vouchInfo"]["user"]]["vouchers"][vouchData["voucherInfo"]["voucher"]]
                except:
                    pass

            #check if user has been vouched to 0 and remove if so
            if vouches[vouchData["vouchInfo"]["user"]]["vouches"] == 0:
                del vouches[vouchData["vouchInfo"]["user"]]
                await ctx.send("Reached 0 vouches. Removed " + vouchData["vouchInfo"]["user"])

            #save vouch data
            jsonHandling.dumpJSON(fname,vouches)
            #remove vouch from buffer
            bufferHandling.removeBuffer(ctx.guild.name.replace(" ",""),"vouches",vouchID)
            await ctx.send("Vouch complete")
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)

    

    @commands.command(name="vouchinfo")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman","3s","2s","1s")
    async def vouchInfo(self, ctx, user:str):

        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
        if os.path.exists(fname):
            vouches = jsonHandling.loadJSON(fname)
        else: 
            await ctx.send("No vouches have been made on this server yet.")
        
        user = user.lower()
        roles = self.getRoles(ctx)
        try:
            embedTitle = "Vouches for " + string.capwords(user)
            embed=discord.Embed(title=embedTitle)

            embed.add_field(name="Vouches", value=vouches[user]["vouches"], inline=False)
            
            try:
                #check if channel has been whitelisted
                if self.whitelistCheck(ctx) == False:
                    pass
                else:
                    #create text string with vouchers info
                    vouchers = ""
                    for k,v in vouches[user]["vouchers"].items():
                        vouchers = vouchers + self.vouchDict[v["value"]] + " " + k 
                        if len(v["reason"]) > 0:
                            vouchers = vouchers + " - " + str(v["reason"]) + "\n"
                        else:
                            vouchers = vouchers + "\n"
                    print ("vouchers",vouchers)
                    embed.add_field(name="Vouchers", value=vouchers, inline=False)

                    #if there is antivouchers
                    print (len(vouches[user]["antivouchers"]))
                    if len(vouches[user]["antivouchers"]) > 0:
                        antivouchers = ""
                        #create text string with antivouchers info
                        for k,v in vouches[user]["antivouchers"].items():
                            antivouchers = antivouchers + self.vouchDict[abs(v["value"])] + " " + k
                            if len(v["reason"]) > 0:
                                antivouchers = antivouchers + " - " + str(v["reason"]) + "\n"
                            else:
                                antivouchers = antivouchers + "\n"
                    else:
                        antivouchers = "None"
                    print ("antivouchers",antivouchers)
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
        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
        if os.path.exists(fname):
            vouches = jsonHandling.loadJSON(fname)
        else: 
            await ctx.send("No vouches have been made on this server yet.")


    @commands.command(name="allvouches")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman","3s","2s","1s")
    async def allvouches(self,ctx):
        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
        if os.path.exists(fname):
            vouches = jsonHandling.loadJSON(fname)
        else: 
            await ctx.send("No vouches have been made on this server yet.")

        try:
            list_vouches = ""
            for k,v in sorted(vouches.items()):
                list_vouches = list_vouches + k.title() + " - " + str(v['vouches'] )+ "\n"

            embed=discord.Embed(title="All 3s Vouches")
            embed.add_field(name = "RSN - # of Vouches", value=list_vouches, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)
            await ctx.send("Couldn't print vouches")

    @commands.command(name="contextinfo")
    async def contextInfo(self,ctx):
        await ctx.send(ctx.message)

    @commands.command(name="addbuffer")
    @commands.has_any_role("Admin",":)")
    async def addBuffer(self,ctx,data):        
        try:
            bufferHandling.addBuffer(ctx.guild.name.replace(" ",""),"vouches",data)
            await ctx.send("All done buddy")
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="viewbuffer")
    @commands.has_any_role("Admin",":)")
    async def viewBuffer(self,ctx):
        try:
            embed = bufferHandling.viewBuffer(ctx.guild.name.replace(" ",""),bufferType="testbuffer",embedTitle="Unconfirmed vouches",embedMessage="Below are the unconfirmed vouches. \n To remove a singular vouch use !removevouch x where x is the vouch ID. \n To remove all vouches use !removevouch all \n To accept a singular vouch use !acceptvouch x where x is the vouch ID. \n To remove all vouches use !removevouch all.")
            await ctx.send(embed=embed)
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="removebuffer")
    @commands.has_any_role("Admin",":)")
    async def removeBuffer(self,ctx,bufferNo): 
        try:   
            bufferHandling.removeBuffer(ctx.guild.name.replace(" ",""),"testbuffer",bufferNo)
            await ctx.send("Removed from buffer.")  
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="removeallbuffer")
    async def removeAllBuffer(self,ctx):
        try:
            bufferHandling.removeBuffer(ctx.guild.name.replace(" ",""),"testbuffer",0)
            await ctx.send("Removed all from buffer.")
        except Exception as e:
            print (e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="acceptbuffer")
    @commands.has_any_role("Admin",":)")
    async def acceptBuffer(self,ctx):
        try:
            buffername = "buffers/" + ctx.guild.name.replace(" ","") +  ".json"    
            print (buffername)
            if os.path.exists(buffername):
                testBuffer = jsonHandling.loadJSON(buffername)
            else: 
                testBuffer = {}    

            for x in list(testBuffer):
                message = "Deleting ",x,testBuffer[x]
                await ctx.send(message)
                del testBuffer[x]
                print (testBuffer)

            jsonHandling.dumpJSON(buffername,testBuffer)
            await ctx.send("Cleared buffer")
        except Exception as e:
            print (e)

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')
        else:
            await ctx.send(error)

def setup(bot):
    bot.add_cog(vouchSystem(bot))