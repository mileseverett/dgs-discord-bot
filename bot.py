import os
import random
import pickle
import string

import discord
from discord.ext import commands
from dotenv import load_dotenv


def dumpPickle(fname,data):
    with open(fname, 'wb') as filehandle:
        pickle.dump(data, filehandle)
    return 

def loadPickle(fname):
    print (fname)
    with open(fname, 'rb') as filehandle:
        print ("ahh")
        data = pickle.load(filehandle)
        print (data)
    return data

def attemptVouch(name,amount,vouches,flipModifier):
    print ("attempting to vouch")
    print ("amount:",amount,"flipmodifier",flipModifier)
    if name in vouches.keys():
        vouches[name]["vouches"] = max(vouches[name]["vouches"] + amount + flipModifier,0)
    else:
        print ("no vouches")
        vouches[name] = {"vouches":max(amount + flipModifier,0),"vouchers":{},"antivouchers":{}}   
    print ("vouch successful")    
    return vouches

def vouchValue(roles):
    value = 0
    if "Floorgazer" in roles:
        value = 3
    elif "Keyer" in roles:
        value = 2
    elif "Wingman" in roles:
        value = 1
    return value

def getRoles(ctx):
    roles = []
    for x in ctx.author.roles:
        roles.append(x.name)
    return roles

def argvCombiner(argv):
    newString = ""
    for x in argv:
        newString = newString + x + " "
    return newString

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!',case_insensitive=True)

@bot.command(name='review')
async def nine_nine(ctx):
    response = "Review!"
    await ctx.send(response)

@bot.command(name="vouch")
@commands.has_any_role("Floorgazer","Keyer","Wingman")
async def vouch(ctx, user:str, *argv):
    user = user.lower()
    antiModifier = 0
    print ("started")
    vouchReason = argvCombiner(argv)

    try:
        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".data"

        if os.path.exists(fname):
            vouches = loadPickle(fname)
        else: 
            vouches = {}

        roles = getRoles(ctx)
        rankValue = vouchValue(roles)

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
                vouches = attemptVouch(user,newRankValue,vouches,antiModifier)
                vouchType = "Vouch update"
            else:
                print ("new vouch")
                vouches = attemptVouch(user,rankValue,vouches,antiModifier)
                vouchType = "Vouch"
        #case where vouches is empty
        except:
            vouches = attemptVouch(user,rankValue,vouches,antiModifier)
            vouchType = "Vouch"

        try:
            del vouches[user]["antivouchers"][authorName]
        except:
            pass

        vouches[user]["vouchers"][authorName] = {
            "value":rankValue,
            "reason":vouchReason[:-1]
        }


        dumpPickle(fname,vouches)

        print ("vouch complete:",vouches)
        await ctx.send(vouchType + " " + user + ". They are now on " + str(vouches[user]["vouches"]))
    except Exception as e:
        print (e)

@bot.command(name="antivouch")
@commands.has_any_role("Floorgazer","Keyer","Wingman")
async def antivouch(ctx, user:str,*argv):
    user = user.lower()
    antiModifier = 0

    vouchReason = argvCombiner(argv)

    try:
        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".data"
        if os.path.exists(fname):
            vouches = loadPickle(fname)
        else: 
            vouches = {}
        print ("loaded vouches",vouches)

        roles = getRoles(ctx)
        rankValue = vouchValue(roles)
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
            vouches = attemptVouch(user,newRankValue*-1,vouches,antiModifier)
            antivouchType = "Antivouch update"
        #if user hasn't antivouched before
        else:
            vouches = attemptVouch(user,rankValue*-1,vouches,antiModifier)
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

        dumpPickle(fname,vouches)
        print ("antivouch complete:",vouches)
        await ctx.send(antivouchType + " " + user + ". They are now on " + str(vouches[user]["vouches"]))
    except Exception as e:
        print (e)

@bot.command(name="vouchinfo")
@commands.has_any_role("Floorgazer","Keyer","Wingman","3s","2s","1s")
async def vouchInfo(ctx, user:str):

    fname = "vouches/" + ctx.guild.name.replace(" ","") + ".data"
    if os.path.exists(fname):
        vouches = loadPickle(fname)
    else: 
        await ctx.send("No vouches have been made on this server yet.")
    
    user = user.lower()
    roles = getRoles(ctx)
    try:
        embedTitle = "Vouches for " + string.capwords(user)
        embed=discord.Embed(title=embedTitle)
        embed.add_field(name="Vouches", value=vouches[user]["vouches"], inline=False)

        vouchDict = {
            1:"<:wingman:722167334688784434>",
            2:"<:keyer:722167334357303368>",
            3:"<:floorgazer:722167334667550741>"
        }

        #display vouch info only to ranks
        if "Floorgazer" in roles or "Keyer" in roles or "Wingman" in roles:
            
            #create text string with vouchers info
            vouchers = ""
            for k,v in vouches[user]["vouchers"].items():
                vouchers = vouchers + vouchDict[v["value"]] + " " + k + " - " + str(v["reason"]) + "\n"
            embed.add_field(name="Vouchers", value=vouchers, inline=False)

            #if there is antivouchers
            if len(vouches[user]["antivouchers"]) > 0:
                antivouchers = ""
                #create text string with antivouchers info
                for k,v in vouches[user]["antivouchers"].items():
                    antivouchers = antivouchers + vouchDict[v["value"]] + " " + k + " - " + str(v["reason"]) + "\n"
            else:
                antivouchers = "None"
            embed.add_field(name="Antivouchers", value=antivouchers, inline=False)
        else:
            pass

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(e)
        await ctx.send("User does not exist")

@bot.command(name="findall")
@commands.has_any_role("Floorgazer","Keyer","Wingman")
async def findAll(ctx):
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
        

@bot.command(name='create-channel')
@commands.has_role('Admin')
async def create_channel(ctx, channel_name="hello"):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@bot.command(name="count")
async def count(ctx, number:int):
    for x in range(number):
        await ctx.send(x)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)