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

def attemptVouch(name,amount,vouches):
    print ("attempting to vouch")
    if name in vouches.keys():
        vouches[name]["vouches"] = max(vouches[name]["vouches"] + amount,0)
    else:
        print ("no vouches")
        vouches[name] = {"vouches":max(amount,0),"vouchers":[],"antivouchers":[]}   
    print ("vouch successful")    
    return vouches

def vouchValue(roles,user,vouches,voucher,antimodifier):
    print ("roles",roles)
    print ("user",user)
    print ("vouches",vouches)
    print ("antimod",antimodifier)
    if "Floorgazer" in roles:
        vouches = attemptVouch(user,3*antimodifier,vouches)
    elif "Keyer" in roles:
        vouches = attemptVouch(user,2*antimodifier,vouches)
    elif "Wingman" in roles:
        vouches = attemptVouch(user,1*antimodifier,vouches)
    print ("after vouches",vouches)
    print ("vouched")
    return vouches

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
    try:
        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".data"

        if os.path.exists(fname):
            vouches = loadPickle(fname)
        else: 
            vouches = {}

        roles = []
        for x in ctx.author.roles:
            roles.append(x.name)
        try:  
            if ctx.author.name in vouches[user]["vouchers"]:
                await ctx.send("Already vouched")
                return
        except:
            pass

        authorName = ctx.author.name
        vouches = vouchValue(roles,user,vouches,authorName,1)
        try:
            vouches[user]["antivouchers"].remove(authorName)
        except:
            pass
        vouches[user]["vouchers"].append(authorName)
        dumpPickle(fname,vouches)
        print ("vouch complete:",vouches)
        await ctx.send("Vouched " + user + ". They are now on " + str(vouches[user]["vouches"]))
    except Exception as e:
        print (e)

@bot.command(name="antivouch")
@commands.has_any_role("Floorgazer","Keyer","Wingman")
async def antivouch(ctx, user:str):
    user = user.lower()
    try:
        fname = "vouches/" + ctx.guild.name.replace(" ","") + ".data"
        if os.path.exists(fname):
            vouches = loadPickle(fname)
        else: 
            vouches = {}
        print ("loaded vouches",vouches)
        roles = []
        for x in ctx.author.roles:
            roles.append(x.name)
        try:
            if ctx.author.name in vouches[user]["antivouchers"]:
                await ctx.send("Already antivouched")
                return
        except:
            pass

        authorName = ctx.author.name
        vouches = vouchValue(roles,user,vouches,authorName,-1)

        try:
            vouches[user]["vouchers"].remove(authorName)
        except:
            pass
        vouches[user]["antivouchers"].append(authorName)

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
@commands.has_any_role("Floorgazer","Keyer","Wingman")
async def vouchInfo(ctx, user:str):

    fname = "vouches/" + ctx.guild.name.replace(" ","") + ".data"
    if os.path.exists(fname):
        vouches = loadPickle(fname)
    else: 
        await ctx.send("No vouches have been made on this server yet.")
    
    user = user.lower()
   
    try:
        embed=discord.Embed()
        embed.add_field(name="Vouches", value=vouches[user]["vouches"], inline=False)
        vouchers = ", ".join(vouches[user]["vouchers"])
        embed.add_field(name="Vouchers", value=vouchers, inline=False)
        if len(vouches[user]["antivouchers"]) > 0:
            antivouchers = ", ".join(vouches[user]["antivouchers"])
        else:
            antivouchers = "None"
        embed.add_field(name="Antivouchers", value=antivouchers, inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(e)
        await ctx.send("User does not exist")

@bot.command(name="findall")
@commands.has_any_role("Floorgazer","Keyer","Wingman")
async def vouchInfo(ctx):
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