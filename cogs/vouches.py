import os
import random
import string
import json
import sys 
import traceback
from datetime import datetime

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

    def attemptVouch(self,name,amount,vouches):
        print("attempting to vouch")
        print("amount:",amount)
        if name in vouches.keys():
            vouches[name]["vouches"] = max(vouches[name]["vouches"] + amount,0)
        else:
            print("no vouches")
            vouches[name] = {"vouches":max(amount,0),"vouchers":{},"antivouchers":{}}   
        print("vouch successful")    
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

    def checkBuffer(self,ctx,user):
        bufferData = bufferHandling.getAllBufferData(ctx.guild.name.replace(" ",""),"vouches")
        for k,v in bufferData.items():
            if v["vouchInfo"]["user"] == user and v["voucherInfo"]["voucher"] == str(ctx.author.id):
                return False
        return True

    def userInBuffer(self,ctx,user):
        bufferData = bufferHandling.getAllBufferData(ctx.guild.name.replace(" ",""),"vouches")
        isInBuffer = False
        for k,v in bufferData.items():
            if v["vouchInfo"]["user"] == user:
                isInBuffer = True
        print(isInBuffer)
        return isInBuffer

    def checkHistory(self,vouchType,vouches,ctx,user):
        
        if self.checkBuffer(ctx,user) == False:
            return False, {"reason":"A vouch from you for this user is already in the buffer awaiting approval."}

        changeBy = 0
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
            prevValue = vouches[user][checkDict][str(ctx.author.id)]["value"]
        #set it to something high
        except:
            prevValue = 1000
            traceback.print_exc(file=sys.stdout)
            
        #check if this user has already vouched AND at the current value
        try:  
            if str(ctx.author.id) in vouches[user][checkDict] and rankValue == prevValue:
                return False, {"reason":"Already vouched this user at current rank value."}
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
            pass
        
        #check to see if this user is flipping their vouch/anti
        try:
            print("oppositeDict=",checkOppositeDict)
            if str(ctx.author.id) in vouches[user][checkOppositeDict]:
                changeBy = vouches[user][checkOppositeDict][str(ctx.author.id)]["value"] 
                print("prevValue",prevValue)
        except Exception as e:
            print(e) 
        print("values",rankValue,prevValue)
        try:
            #check if vouch is an update or not
            if str(ctx.author.id) in vouches[user][checkDict] and rankValue > prevValue:
                changeBy = vouches[user][checkDict][str(ctx.author.id)]["value"]          
        except Exception as ಠ_ಠ:
            print(ಠ_ಠ)
            traceback.print_exc(file=sys.stdout)

        now = datetime.now()

        vouchInfo = {
            "user":user,
            "rankValue":rankValue,
            "changeBy":(changeBy + rankValue)*anti,
            "vouchType":vouchType,
            "vouchTimestamp":now.strftime("%d/%m/%Y, %H:%M:%S")
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
        print(settings)
        print(ctx.message.channel.id)
        if ctx.message.channel.id in settings["whitelistedChannels"]:
            return True
        else:
            return False

    @commands.command(name="updatingmessageinit")
    async def updatingmessage(self,ctx):
        #delete the senders message
        usersMessage = ctx.message
        await usersMessage.delete()
        
        #create a new message and send it
        message = await ctx.send(embed=discord.Embed(title="Type update message to initalise me."))
        
        #store the details of the sent message
        updatingVouchMessage = {
            "messageID":message.id,
            "channelID":message.channel.id
        }

        #load server settings
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)

        #update details of updating vouch message
        settings["updatingVouchMessage"] = updatingVouchMessage
        
        #save details
        jsonHandling.dumpJSON(fname,settings)


    @commands.command(name="updatemessage")
    async def updateMessage(self,ctx):
        #load server settings
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)
        
        #delete the message that sent this command
        usersMessage = ctx.message
        await usersMessage.delete()

        #find the channel + message ID that will be updated
        channel = self.bot.get_channel(settings["updatingVouchMessage"]["channelID"])
        message = await channel.fetch_message(settings["updatingVouchMessage"]["messageID"])
        
        #get the allVouches message
        newmessage = await self.allVouches(ctx,True)
        
        #edit the message with the new embed
        await message.edit(embed=newmessage)


    @commands.command(name="vouch")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman")
    async def vouch(self, ctx, user:str, *argv):
        if self.whitelistCheck(ctx) == False:
            await ctx.send("Cannot do that in this channel")
            return
        try:
            user = user.lower()
            vouchReason = self.argvCombiner(argv)
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            acceptableVouch, vouchInfo = self.checkHistory("vouch",vouches,ctx,user)
            if acceptableVouch == False:
                await ctx.send(vouchInfo["reason"])
                return
            print(acceptableVouch,vouchInfo)
            authorName = str(ctx.author.id)

            voucherInfo = {
                "value":vouchInfo["rankValue"],
                "reason":vouchReason[:-1],
                "voucher":authorName,
                "voucherName":ctx.author.name    
            }

            bufferData = {
                "vouchInfo":vouchInfo,
                "voucherInfo":voucherInfo
            }

            bufferHandling.addBuffer(ctx.guild.name.replace(" ",""),"vouches",bufferData)
            await ctx.send("Your vouch for " + user + " has been added to the queue to be reviewed by admins.")
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        
    @commands.command(name="antivouch")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman")
    async def antivouch(self, ctx, user:str,*argv):
        if self.whitelistCheck(ctx) == False:
            await ctx.send("Cannot do that in this channel")
            return
        try:
            user = user.lower()
            vouchReason = self.argvCombiner(argv)
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            vouches = jsonHandling.loadJSON(fname)

            if user not in vouches.keys() and self.userInBuffer(ctx,user) == False:
                await ctx.send("They don't have any vouches you dumbfuck.")
                return
            acceptableVouch, vouchInfo = self.checkHistory("antivouch",vouches,ctx,user)
            if acceptableVouch == False:
                await ctx.send(vouchInfo["reason"])
                return
            print(acceptableVouch,vouchInfo)
            authorName = str(ctx.author.id)
            voucherInfo = {
                "value":vouchInfo["rankValue"],
                "reason":vouchReason[:-1],
                "voucher":authorName,
                "voucherName":ctx.author.name    
            }
            bufferData = {
                "vouchInfo":vouchInfo,
                "voucherInfo":voucherInfo
            }
            bufferHandling.addBuffer(ctx.guild.name.replace(" ",""),"vouches",bufferData)
            await ctx.send("Your vouch for " + user + " has been added to the queue to be reviewed by admins.")
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="adminvouch")
    async def adminVouch(self,ctx,voucher:int,user:str,vouchType:str,rankValue:int,reason:str):
        vouchType = vouchType.lower()
        if vouchType == "vouch":
            anti = 1
        elif vouchType == "antivouch":
            anti = -1
        
        now = datetime.now()

        vouchInfo = {
            "user":user.lower(),
            "rankValue":rankValue,
            "changeBy":rankValue * anti,
            "vouchType":vouchType,
            "vouchTimestamp":now.strftime("%d/%m/%Y, %H:%M:%S")
        }

        for x in ctx.guild.members:
            if x.id == voucher:
                voucherName = x.name
                break

        voucherInfo = {
            "value":rankValue,
            "reason":reason,
            "voucher":voucher,
            "voucherName":x.name
        }

        bufferData = {
            "vouchInfo":vouchInfo,
            "voucherInfo":voucherInfo
        }

        bufferHandling.addBuffer(ctx.guild.name.replace(" ",""),"vouches",bufferData)
        await ctx.send("Your vouch for " + user + " has been added to the queue to be reviewed by admins.")


    @commands.command(name="removeuser")
    async def removeUser(self,ctx,user:str):
        if self.whitelistCheck(ctx) == False:
                await ctx.send("This command is not allowed in this channel.")
        else:
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            del vouches[user.lower()]
            jsonHandling.dumpJSON(fname,vouches)
            await ctx.send(user + " was completely removed from the vouch list.")

    @commands.command(name="vouchbuffer")
    async def viewVouchBuffer(self,ctx):
        try:
            if self.whitelistCheck(ctx) == False:
                await ctx.send("This command is not allowed in this channel.")
            else:
                bufferData = bufferHandling.getAllBufferData(ctx.guild.name.replace(" ",""),"vouches")
                print(bufferData)
                embed = discord.Embed(title="Vouches Buffer")
                for k,v in bufferData.items():
                    if len(v["voucherInfo"]["reason"]) > 0:
                        reason = v["voucherInfo"]["reason"]
                    else:
                        reason = "None given"
                    vouchLine = self.vouchDict[abs(v["vouchInfo"]["rankValue"])] + v["voucherInfo"]["voucherName"] + " " + v["vouchInfo"]["vouchType"] + "ed " + string.capwords(v["vouchInfo"]["user"]) + "\n" + v["vouchInfo"]["vouchTimestamp"] + "\n" + "Reason: " + reason
                    embed.add_field(name=k, value=vouchLine, inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="removevouch")
    async def removeVouch(self,ctx,vouchID:str):
        try:   
            if self.whitelistCheck(ctx) == False:
                await ctx.send("This command is not allowed in this channel.")
            else:
                bufferHandling.removeBuffer(ctx.guild.name.replace(" ",""),"vouches",vouchID)
                await ctx.send("Removed from buffer.")  
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="acceptallvouches")
    async def acceptAllVouches(self,ctx):
        if self.whitelistCheck(ctx) == False:
            await ctx.send("This command is not allowed in this channel.")
        else:
            IDs = bufferHandling.getBufferIDs(ctx.guild.name.replace(" ",""),"vouches")
            for x in IDs:
                await self.acceptVouch(ctx,x, True)
            await ctx.send("All done.")

    @commands.command(name="acceptvouch")
    async def acceptVouch(self,ctx,vouchID:str,silent=False):
        try:
            #Message to be printed out at the end.
            message = "Vouch complete!"
            #get data for this vouchID
            vouchData = bufferHandling.getBufferData(ctx.guild.name.replace(" ",""),"vouches",vouchID)
            #get vouches data
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            #add the vouch to the vouch datastore
            vouches = self.attemptVouch(vouchData["vouchInfo"]["user"],vouchData["vouchInfo"]["changeBy"],vouches)          
           
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
                message = ("Reached 0 vouches. Removed " + vouchData["vouchInfo"]["user"])
                silent = False

            #save vouch data
            jsonHandling.dumpJSON(fname,vouches)
            #remove vouch from buffer
            bufferHandling.removeBuffer(ctx.guild.name.replace(" ",""),"vouches",vouchID)
            # await self.updateMessage(ctx)
            if silent == False:
                await ctx.send(message)
            else:
                return
        except KeyError:
            await ctx.send("No vouch with ID:"+vouchID  + " exists in the buffer.")
        except Exception as e:
            print(e)
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
                        vouchers = vouchers + self.vouchDict[v["value"]] + " " + v["voucherName"] 
                        if len(v["reason"]) > 0:
                            vouchers = vouchers + " - " + str(v["reason"]) + "\n"
                        else:
                            vouchers = vouchers + "\n"
                    print("vouchers",vouchers)
                    embed.add_field(name="Vouchers", value=vouchers, inline=False)

                    #if there is antivouchers
                    print(len(vouches[user]["antivouchers"]))
                    if len(vouches[user]["antivouchers"]) > 0:
                        antivouchers = ""
                        #create text string with antivouchers info
                        for k,v in vouches[user]["antivouchers"].items():
                            antivouchers = antivouchers + self.vouchDict[abs(v["value"])] + " " + v["voucherName"]
                            if len(v["reason"]) > 0:
                                antivouchers = antivouchers + " - " + str(v["reason"]) + "\n"
                            else:
                                antivouchers = antivouchers + "\n"
                    else:
                        antivouchers = "None"
                    print("antivouchers",antivouchers)
                    embed.add_field(name="Antivouchers", value=antivouchers, inline=False)
            except:
                pass
            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send(user + " has no vouches.")

        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="allvouches")
    @commands.has_any_role("Floorgazer","Keyer","Wingman","Wingwoman","3s","2s","1s")
    async def allVouches(self,ctx,silent=False):
        try:
            fname = "vouches/" + ctx.guild.name.replace(" ","") + ".json"
            if os.path.exists(fname):
                vouches = jsonHandling.loadJSON(fname)
            else: 
                await ctx.send("No vouches have been made on this server yet.")
            embed=discord.Embed(title="All 3s Vouches")
            if len(vouches) == 0:
                embed.add_field(name="no vouches",value="no vouches",inline=False)
                return embed

            listVouches = ""
            for k,v in sorted(vouches.items()):
                listVouches = listVouches + k.title() + " - " + str(v['vouches'] )+ "\n"
            embed.add_field(name = "RSN - # of Vouches", value=listVouches, inline=False)
            if silent == False:
                await ctx.send(embed=embed)
            else:
                return embed
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
            await ctx.send("Couldn't printvouches")

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')
        else:
            await ctx.send(error)

def setup(bot):
    bot.add_cog(vouchSystem(bot))