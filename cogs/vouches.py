import os
import string
import json
import sys
import traceback
from datetime import datetime

import discord
from discord.ext import commands

from utilities import jsonHandling, bufferHandling
from utilities.misc import createFolder

class vouchSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.vouchDict = {
                1:"<:wingman:722167334688784434>",
                2:"<:keyer:722167334357303368>",
                3:"<:floorgazer:722167334667550741>"
            }
        createFolder("vouches")

    def addVouchee(self, name, vouches):
        """
        Helper function to add a new vouchee

        Parameters:
        name - string name of the vouchee
        vouches - dictionary of the form {vouches, vouchers, antivouchers}
            - vouches is the numeric number of vouches
            - vouchers is a list of names of vouchers
            - antivouches is a list of names of antivouches

        """
        print("attempting to vouch")
        if name in vouches.keys():
            pass
        else:
            print("no vouches - adding to JSON")
            vouches[name] = {"vouches":0, "vouchers":{}, "antivouchers":{}}   
        print("added vouchee successfully")
        return vouches

    def vouchValue(self, roles):
        """
        Helper function to define values of DGS ranks

        Parameters:
        roles - list of DGS ranks from getRoles()
        """
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

    def getRoles(self, ctx):
        """
        Helper function to get the roles for rank values

        """
        roles = []
        for x in ctx.author.roles:
            roles.append(x.name)
        return roles

    def checkBuffer(self, ctx, user):
        """
        Helper function to check if the caller has already made a vouch or antivouch in the buffer

        Parameters:
        user - string name of the vouchee 

        """
        bufferData = bufferHandling.getAllBufferData(ctx.guild.name.replace(" ",""), "vouches")
        for k,v in bufferData.items():
            if v["vouchInfo"]["user"] == user and v["voucherInfo"]["voucher"] == str(ctx.author.id):
                return False
        return True

    def userInBuffer(self, ctx, user):
        """
        Helper function to check if a user is in the buffer already

        Parameters:
        user - string name of the vouchee 

        """
        bufferData = bufferHandling.getAllBufferData(ctx.guild.name.replace(" ",""), "vouches")
        isInBuffer = False
        for k,v in bufferData.items():
            if v["vouchInfo"]["user"] == user:
                isInBuffer = True
        return isInBuffer

    def checkHistory(self, vouchType, vouches, ctx, user):
        """
        Helper function to prepare vouches

        Parameters:
        vouchType - string that is one of: "vouch" or "antivouch"
        vouches - dictionary of the form {vouches, vouchers, antivouchers}
            - vouches is the numeric number of vouches
            - vouchers is a list of names of vouchers
            - antivouches is a list of names of antivouches

        """
        if self.checkBuffer(ctx, user) == False:
            return False, {"reason":"A vouch from you for this user is already in the buffer awaiting approval."}

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
            
        # check if this user has already vouched AND at the current value
        try:  
            if str(ctx.author.id) in vouches[user][checkDict] and rankValue == vouches[user][checkDict][str(ctx.author.id)]["value"]:
                return False, {"reason":"Already vouched this user at current rank value."}
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
            pass

        now = datetime.now()

        vouchInfo = {
            "user":user,
            "rankValue":rankValue,
            "vouchType":vouchType,
            "vouchTimestamp":now.strftime("%d/%m/%Y, %H:%M:%S")
        }       

        return True, vouchInfo

    def argvCombiner(self, argv):
        """
        Helper function to combine list elements

        Parameters:
        argv - list of arguments to combine

        """
        newString = ""
        for x in argv:
            newString = newString + x + " "
        return newString

    def whitelistCheck(self, ctx):
        """
        Helper function to check if this channel is whitelisted to accept vouch commands

        """
        fname = "guildsettings/" + ctx.guild.name.replace(" ", "") + ".json"
        settings = jsonHandling.loadJSON(fname)
        print(settings)
        print(ctx.message.channel.id)
        if ctx.message.channel.id in settings["whitelistedChannels"]:
            return True
        else:
            return False

    @commands.command(name="updatingmessageinit")
    @commands.has_any_role("Reviewer","Admin")
    async def updatingmessage(self, ctx):
        """
        Callable function to create a table that can be filled with vouches

        """
        print("------------------------------ beginning updatingmessage() ------------------------------")
        # delete the senders message
        usersMessage = ctx.message
        await usersMessage.delete()
        
        # create a new message and send it
        message = await ctx.send(embed=discord.Embed(title="Type update message to initalise me."))
        
        # store the details of the sent message
        updatingVouchMessage = {
            "messageID":message.id,
            "channelID":message.channel.id
        }

        # load server settings
        fname = "guildsettings/" + ctx.guild.name.replace(" ","") + ".json"
        settings = jsonHandling.loadJSON(fname)

        # update details of updating vouch message
        settings["updatingVouchMessage"] = updatingVouchMessage
        
        # save details
        jsonHandling.dumpJSON(fname, settings)
        print("------------------------------ ending updatingmessage() ------------------------------")


    @commands.command(name="updatemessage")
    @commands.has_any_role("Reviewer","Admin")
    async def updateMessage(self, ctx):
        """
        Callable function to update the table to the latest vouches

        """
        print("------------------------------ beginning updateMessage() ------------------------------")
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
        newmessage = await self.allVouches(ctx, True)
        
        #edit the message with the new embed
        await message.edit(embed=newmessage)
        print("------------------------------ ending updateMessage() ------------------------------")


    @commands.command(name="vouch")
    @commands.has_any_role("Floorgazer", "Keyer", "Wingman", "Wingwoman")
    async def vouch(self, ctx, user:str, *argv):
        """
        Callable function for a DGS rank to vouch someone

        Parameters:
        user - string of the name of the vouchee
        *argv - additional arguments. Intended as a description of the reasoning for a vouch

        """
        print("------------------------------ beginning vouch() ------------------------------")
        if self.whitelistCheck(ctx) == False:
            await ctx.send("Cannot do that in this channel")
            return
        try:
            user = user.lower()
            vouchReason = self.argvCombiner(argv)
            fname = "vouches/" + ctx.guild.name.replace(" ", "") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            acceptableVouch, vouchInfo = self.checkHistory("vouch", vouches, ctx, user)
            if acceptableVouch == False:
                await ctx.send(vouchInfo["reason"])
                return
            print(acceptableVouch, vouchInfo)
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

            bufferHandling.addBuffer(ctx.guild.name.replace(" ",""), "vouches", bufferData)
            await ctx.send("Your vouch for " + user + " has been added to the queue to be reviewed by admins.")
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        print("------------------------------ ending vouch() ------------------------------")
        
    @commands.command(name="antivouch")
    @commands.has_any_role("Floorgazer", "Keyer", "Wingman", "Wingwoman")
    async def antivouch(self, ctx, user:str, *argv):
        """
        Callable function for a DGS rank to antivouch someone

        Parameters:
        user - string of the name of the vouchee
        *argv - additional arguments. Intended as a description of the reasoning for a antivouch

        """
        print("------------------------------ beginning antivouch() ------------------------------")
        if self.whitelistCheck(ctx) == False:
            await ctx.send("Cannot do that in this channel")
            return
        try:
            user = user.lower()
            vouchReason = self.argvCombiner(argv)
            fname = "vouches/" + ctx.guild.name.replace(" ", "") + ".json"
            vouches = jsonHandling.loadJSON(fname)

            if user not in vouches.keys() and self.userInBuffer(ctx, user) == False:
                await ctx.send("They don't have any vouches you dumbfuck.")
                return
            acceptableVouch, vouchInfo = self.checkHistory("antivouch", vouches, ctx, user)
            if acceptableVouch == False:
                await ctx.send(vouchInfo["reason"])
                return
            print(acceptableVouch, vouchInfo)
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

            bufferHandling.addBuffer(ctx.guild.name.replace(" ", ""), "vouches", bufferData)
            await ctx.send("Your vouch for " + user + " has been added to the queue to be reviewed by admins.")
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        print("------------------------------ ending antivouch() ------------------------------")

    @commands.command(name="unvouch")
    @commands.has_any_role("Floorgazer", "Keyer", "Wingman", "Wingwoman")
    async def unvouch(self, ctx, user:str):
        """
        Callable function for a DGS rank to unvouch someone they previously unvouched

        Parameters:
        user - string of the name of the vouchee
        *argv - additional arguments. Intended as a description of the reasoning for a antivouch

        """
        print("------------------------------ beginning unvouch() ------------------------------")
        if self.whitelistCheck(ctx) == False:
            await ctx.send("Cannot do that in this channel")
            return
        try:
            user = user.lower()
            fname = "vouches/" + ctx.guild.name.replace(" ", "") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            print(vouches)

            authorName = str(ctx.author.id)

            if user not in vouches.keys() or (user in vouches.keys() and authorName not in vouches[user]["vouchers"]):
                await ctx.send("You haven't vouched them.")
            
            if user in vouches.keys() and authorName in vouches[user]["vouchers"]:
                vouches[user]['vouches'] = vouches[user]['vouches'] - vouches[user]['vouchers'][authorName]['value']
                if vouches[user]['vouches'] <= 0:
                    ctx.send("Vouchee is at 0 or below - removing from vouch list")
                    await self.removeUser(ctx, user)
                else:
                    del vouches[user]['vouchers'][authorName]
                    jsonHandling.dumpJSON(fname, vouches)
                    await ctx.send("Vouch successfully removed.")
            
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        
        print("------------------------------ ending unvouch() ------------------------------")

    @commands.command(name="adminvouch")
    @commands.has_any_role("Reviewer", "Admin")
    async def adminVouch(self, ctx, voucher:int, user:str, vouchType:str, rankValue:int, reason:str):
        """
        Callable function for an admin to do a vouch or antivouch*

        Parameters:
        voucher - Int of discord ID number of the person you are vouching for
        user - String of the name of the vouchee/antivouchee
        vouchType - String of "vouch" or "antivouch"
        rankValue - Int of value of the rank of the voucher
        reason - String message of the reasoning

        """
        print("------------------------------ beginning adminVouch() ------------------------------")
        vouchType = vouchType.lower()
        now = datetime.now()

        vouchInfo = {
            "user":user.lower(),
            "rankValue":rankValue,
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

        bufferHandling.addBuffer(ctx.guild.name.replace(" ",""), "vouches", bufferData)
        await ctx.send("Your vouch for " + user + " has been added to the queue to be reviewed by admins.")
        print("------------------------------ ending adminVouch() ------------------------------")

    @commands.command(name="renamevouchee")
    @commands.has_any_role("Reviewer","Admin")
    async def renameVouchee(self, ctx, user:str, newName:str):
        """
        Callable function for an admin to rename a vouchee in the system

        Parameters:
        user - String of the name of the vouchee/antivouchee in the system
        newName - String of the new name to use

        """
        print("------------------------------ beginning renameVouchee() ------------------------------")
        if self.whitelistCheck(ctx) == False:
            await ctx.send("This command is not allowed in this channel.")
        
        fname = "vouches/" + ctx.guild.name.replace(" ", "") + ".json"
        vouches = jsonHandling.loadJSON(fname)
        
        data = vouches.pop(user.lower())
        vouches[newName.lower()] = data

        jsonHandling.dumpJSON(fname,vouches)

        await ctx.send("Rename complete.")
        print("------------------------------ ending renameVouchee() ------------------------------")

    @commands.command(name="removeuser")
    @commands.has_any_role("Reviewer", "Admin")
    async def removeUser(self, ctx, user:str):
        """
        Callable function for an admin to remove a vouchee from the system

        Parameters:
        user - String of the name of the vouchee/antivouchee

        """
        print("------------------------------ beginning viewVouchBuffer() ------------------------------")
        if self.whitelistCheck(ctx) == False:
                await ctx.send("This command is not allowed in this channel.")
        else:
            fname = "vouches/" + ctx.guild.name.replace(" ", "") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            del vouches[user.lower()]
            jsonHandling.dumpJSON(fname, vouches)
            await ctx.send(user + " was completely removed from the vouch list.")
        print("------------------------------ ending viewVouchBuffer() ------------------------------")

    @commands.command(name="vouchbuffer")
    @commands.has_any_role("Floorgazer", "Keyer", "Wingman", "Wingwoman", "3s", "2s", "1s")
    async def viewVouchBuffer(self, ctx):
        """
        Callable function to see the vouches in a buffer

        """
        print("------------------------------ beginning viewVouchBuffer() ------------------------------")
        try:
            if self.whitelistCheck(ctx) == False:
                await ctx.send("This command is not allowed in this channel.")
            else:
                bufferData = bufferHandling.getAllBufferData(ctx.guild.name.replace(" ", ""), "vouches")
                print(bufferData)
                if not bufferData:
                    await ctx.send("Vouch buffer is empty!")
                else:
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
        print("------------------------------ ending viewVouchBuffer() ------------------------------")

    @commands.command(name="removebuffervouch")
    @commands.has_any_role("Reviewer", "Admin")
    async def removeVouch(self, ctx, vouchID:str, silent = False):
        """
        Callable function for admin's to remove a vouch or antivouch from the buffer

        Parameters:
        vouchID - String corresponding to the ID of the vouch to remove

        """
        print("------------------------------ beginning removeVouch() ------------------------------")
        try:   
            if self.whitelistCheck(ctx) == False:
                await ctx.send("This command is not allowed in this channel.")
            else:
                bufferHandling.removeBuffer(ctx.guild.name.replace(" ",""), "vouches", vouchID)
                if silent == False:
                    await ctx.send("Removed from buffer.") 
                else:
                    return
                
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        
        print("------------------------------ ending removeVouch() ------------------------------")

    @commands.command(name="acceptallvouches")
    @commands.has_any_role("Reviewer", "Admin")
    async def acceptAllVouches(self, ctx):
        """
        Callable function for admin's to blanket accept all vouches and antivouches existing in the buffer, without needing to specify any IDs

        """
        print("------------------------------ beginning acceptAllVouches() ------------------------------")
        if self.whitelistCheck(ctx) == False:
            await ctx.send("This command is not allowed in this channel.")
        else:
            IDs = bufferHandling.getBufferIDs(ctx.guild.name.replace(" ", ""), "vouches")
            if not IDs:
                await ctx.send("Nothing in the buffer!")
            else:
                for x in IDs:
                    await self.acceptVouch(ctx, x, True)
                await ctx.send("All done.")
        print("------------------------------ ending acceptAllVouches() ------------------------------")
    
    @commands.command(name="rejectallvouches")
    @commands.has_any_role("Reviewer", "Admin")
    async def rejectAllVouches(self, ctx):
        """
        Callable function for admin's to blanket reject all vouches and antivouches existing in the buffer, without needing to specify any IDs

        """
        print("------------------------------ beginning rejectAllVouches() ------------------------------")
        if self.whitelistCheck(ctx) == False:
            await ctx.send("This command is not allowed in this channel.")
        else:
            IDs = bufferHandling.getBufferIDs(ctx.guild.name.replace(" ", ""), "vouches")
            if not IDs:
                await ctx.send("Nothing in the buffer!")
            else:
                for x in IDs:
                    await self.removeVouch(ctx, x, True)
                await ctx.send("All done.")
        print("------------------------------ ending rejectAllVouches() ------------------------------")

    @commands.command(name="acceptvouch")
    @commands.has_any_role("Reviewer", "Admin")
    async def acceptVouch(self, ctx, vouchID:str, silent=False):
        """
        Callable function for admin's to accept a vouch from the buffer based on ID

        Parameters:
        vouchID - String representing the vouch to accept
        silent - Boolean indicating whether or not to get verbose information

        """
        try:
            print("------------------------------ beginning acceptVouch() ------------------------------")
            # Message to be printed out at the end.
            message = "Vouch complete!"
            # get data for this vouchID
            vouchData = bufferHandling.getBufferData(ctx.guild.name.replace(" ",""), "vouches", vouchID)
            # get vouches data
            fname = "vouches/" + ctx.guild.name.replace(" ", "") + ".json"
            vouches = jsonHandling.loadJSON(fname)
            # add the vouch to the vouch datastore
            vouches = self.addVouchee(vouchData["vouchInfo"]["user"],vouches)
           
            # Remove any instances of this person already vouching/anti'ing the vouchee
            # We will update with their new information (new vouch/anti and rank value)
            try:
                del vouches[vouchData["vouchInfo"]["user"]]["antivouchers"][vouchData["voucherInfo"]["voucher"]]
                print("removing exisiting antivouch entry")
            except:
                pass

            try:
                del vouches[vouchData["vouchInfo"]["user"]]["vouchers"][vouchData["voucherInfo"]["voucher"]]
                print("removing exisiting vouch entry")
            except:
                pass
            
            # add the voucher info to the vouch datastore
            # if it's a vouch
            if vouchData["vouchInfo"]["vouchType"] == "vouch":
                vouches[vouchData["vouchInfo"]["user"]]["vouchers"][vouchData["voucherInfo"]["voucher"]] = vouchData["voucherInfo"]
                
            # if it's an antivouch
            elif vouchData["vouchInfo"]["vouchType"] == "antivouch":
                vouches[vouchData["vouchInfo"]["user"]]["antivouchers"][vouchData["voucherInfo"]["voucher"]] = vouchData["voucherInfo"]
            
            # Update the number of vouches
            numVouches = 0
            for voucher in vouches[vouchData["vouchInfo"]["user"]]['vouchers']:
                numVouches += vouches[vouchData["vouchInfo"]["user"]]['vouchers'][voucher]['value']
            
            for antivoucher in vouches[vouchData["vouchInfo"]["user"]]['antivouchers']:
                numVouches -= vouches[vouchData["vouchInfo"]["user"]]['antivouchers'][antivoucher]['value']
            
            # Add to dict
            vouches[vouchData["vouchInfo"]["user"]]["vouches"] = max(numVouches, 0)

            #c heck if user has been vouched to 0 and remove if so
            if vouches[vouchData["vouchInfo"]["user"]]["vouches"] == 0:
                del vouches[vouchData["vouchInfo"]["user"]]
                message = ("Reached 0 vouches. Removed " + vouchData["vouchInfo"]["user"])
                silent = False

            # save vouch data
            jsonHandling.dumpJSON(fname,vouches)
            # remove vouch from buffer
            bufferHandling.removeBuffer(ctx.guild.name.replace(" ", ""), "vouches", vouchID)
            # await self.updateMessage(ctx)
            if silent == False:
                await ctx.send(message)
            else:
                return
            print("------------------------------ ending acceptVouch() ------------------------------")
        except KeyError:
            await ctx.send("No vouch with ID:"+vouchID  + " exists in the buffer.")
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)

    @commands.command(name="vouchinfo")
    @commands.has_any_role("Floorgazer", "Keyer", "Wingman", "Wingwoman", "3s", "2s", "1s")
    async def vouchInfo(self, ctx, user:str):
        """
        Callable function for seeing information about the vouches of a user. Functionality gives verbose output for Wing+ in whitelisted channels and returns only the number of vouches in other cases.

        Parameters:
        user - string of the vouchee name to display

        """
        print("------------------------------ begining vouchInfo() ------------------------------")
        fname = "vouches/" + ctx.guild.name.replace(" ", "") + ".json"
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
                    print("vouchers", vouchers)
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
                    print("antivouchers", antivouchers)
                    embed.add_field(name="Antivouchers", value=antivouchers, inline=False)
            except:
                pass
            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send(user + " has no vouches.")

        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        
        print("------------------------------ ending vouchInfo() ------------------------------")

    @commands.command(name="allvouches")
    @commands.has_any_role("Floorgazer", "Keyer", "Wingman", "Wingwoman", "3s", "2s", "1s")
    async def allVouches(self, ctx, silent=False):
        """
        Callable function for seeing information about all vouchees. Functionality gives in-depth output for Wing+ in whitelisted channels and returns only the number of vouches in other cases.

        Parameters:
        silent - Boolean indicating whether or not to get verbose information

        """
        print("------------------------------ beginning allVouches() ------------------------------")
        try:
            fname = "vouches/" + ctx.guild.name.replace(" ", "") + ".json"
            if os.path.exists(fname):
                vouches = jsonHandling.loadJSON(fname)
            else: 
                await ctx.send("No vouches have been made on this server yet.")
            embed=discord.Embed(title="All 3s Vouches")
            if len(vouches) == 0:
                embed.add_field(name="no vouches", value="no vouches", inline=False)
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
        
        print("------------------------------ ending allVouches() ------------------------------")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')
        else:
            await ctx.send(error)

def setup(bot):
    bot.add_cog(vouchSystem(bot))