import os
import random
import pickle

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

def vouchValue(roles,user,vouches,voucher,antiModifier,flipModifier):
    print ("roles",roles)
    print ("user",user)
    print ("vouches",vouches)
    print ("antimod",antiModifier)
    if "Floorgazer" in roles:
        vouches = attemptVouch(user,rankValue*antiModifier,vouches,flipModifier)
    elif "Keyer" in roles:
        vouches = attemptVouch(user,rankValue*antiModifier,vouches,flipModifier)
    elif "Wingman" in roles:
        vouches = attemptVouch(user,1*antiModifier,vouches,flipModifier)
    print ("after vouches",vouches)
    print ("vouched")
    return vouches

def returnHighestRole(roles):
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

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!',case_insensitive=True)

@bot.command(name='review')
async def nine_nine(ctx):
    response = "Review!"
    await ctx.send(response)

@bot.command(name="vouch")
@commands.has_any_role("Floorgazer","Keyer","Wingman")
async def vouch(ctx, user:str):
    user = user.lower()
    antiModifier = 0
    try:
        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".data"

        if os.path.exists(fname):
            vouches = loadPickle(fname)
        else: 
            vouches = {}

        roles = getRoles(ctx)

        try:  
            if ctx.author.name in vouches[user]["vouchers"]:
                await ctx.send("Already vouched")
                return
        except:
            pass

        try:
            if ctx.author.name in vouches[user]["antivouchers"]:
                antiModifier = vouches[user]["antivouchers"][ctx.author.name]
        except: 
            pass

        authorName = ctx.author.name
        # vouches = vouchValue(roles,user,vouches,authorName,1,antiModifier)
        rankValue = returnHighestRole(roles)
        vouches = attemptVouch(user,rankValue,vouches,antiModifier)
        try:
            del vouches[user]["antivouchers"][authorName]
        except:
            pass

        vouches[user]["vouchers"][authorName] = rankValue

        dumpPickle(fname,vouches)

        print ("vouch complete:",vouches)
        await ctx.send("Vouched " + user + ". They are now on " + str(vouches[user]["vouches"]))
    except Exception as e:
        print (e)

@bot.command(name="antivouch")
@commands.has_any_role("Floorgazer","Keyer","Wingman")
async def antivouch(ctx, user:str):
    user = user.lower()
    antiModifier = 0
    try:
        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".data"
        if os.path.exists(fname):
            vouches = loadPickle(fname)
        else: 
            vouches = {}
        print ("loaded vouches",vouches)

        roles = getRoles(ctx)

        try:
            if ctx.author.name in vouches[user]["antivouchers"]:
                await ctx.send("Already antivouched")
                return
        except:
            pass

        #checks if this user previously vouched them
        try:
            if ctx.author.name in vouches[user]["vouchers"]:
                antiModifier = vouches[user]["vouchers"][ctx.author.name] * -1
        except: 
            pass
        
        authorName = ctx.author.name
        rankValue = returnHighestRole(roles)
        vouches = attemptVouch(user,rankValue*-1,vouches,antiModifier)
        try:
            del vouches[user]["vouchers"][authorName]
        except:
            pass

        vouches[user]["antivouchers"][authorName] = rankValue

        #check if user has been vouched to 0 and remove if so
        if vouches[user]["vouches"] == 0:
            del vouches[user]
            await ctx.send("Reached 0 vouches. Removed " + user)

        dumpPickle(fname,vouches)
        print ("antivouch complete:",vouches)
        await ctx.send("Antivouched " + user + ". They are now on " + str(vouches[user]["vouches"]))
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
        embedTitle = "Vouches for " + user
        embed=discord.Embed(title=embedTitle)
        embed.add_field(name="Vouches", value=vouches[user]["vouches"], inline=False)

        vouchDict = {
            1:"<:wingman:722167334688784434>",
            2:"<:keyer:722167334357303368>",
            3:"<:floorgazer:722167334667550741>"
        }


        print (user)
        #display vouch info only to ranks
        if "Floorgazer" in roles or "Keyer" in roles or "Wingman" in roles:
            
            #create text string with 
            vouchers = ""
            for k,v in vouches[user]["vouchers"].items():
                vouchers = vouchers + vouchDict[v] + " " + k + "\n"
            embed.add_field(name="Vouchers", value=vouchers, inline=False)


            if len(vouches[user]["antivouchers"]) > 0:
                antivouchers = ""
                for k,v in vouches[user]["antivouchers"].items():
                    antivouchers = antivouchers + vouchDict[v] + " " + k + "\n"
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


# @bot.command(name="emojiNames")
# async def emojiNames(ctx):



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)