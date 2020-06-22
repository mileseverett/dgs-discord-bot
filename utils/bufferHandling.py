import os
import random
import string
import json
import sys, traceback

from discord import Embed
from utils import jsonHandling

def addBuffer(serverName,bufferType,data):
    
    #generate filename of settings file
    settingsFileName = "guildsettings/" + serverName + ".json"

    #load settings info
    if os.path.exists(settingsFileName):
        settings = jsonHandling.loadJSON(settingsFileName)
    else: 
        settings = {}

    #determine which ID to grab
    IDType = bufferType + "IDcounter"

    #get unique ID of new buffer item
    try: 
        ID = settings[IDType]
        settings[IDType] = settings[IDType] + 1
    except Exception as e:
        print (e)
        ID = 1
        settings[IDType] = ID + 1

    #update settings file
    jsonHandling.dumpJSON(settingsFileName,settings)

    #generate filename of buffer file for this server + buffer type
    buffername = "buffers/" + serverName + bufferType + ".json"    
    print ("buffername",buffername)
    #load buffer
    if os.path.exists(buffername):
        testBuffer = jsonHandling.loadJSON(buffername)
    else: 
        testBuffer = {}    

    #add data to the buffer at correct ID
    testBuffer[ID] = data

    #save the buffer data
    jsonHandling.dumpJSON(buffername,testBuffer)
    return

def viewBuffer(serverName, bufferType, embedTitle, embedMessage):
    buffername = "buffers/" + serverName + bufferType +  ".json"    
    testBuffer = jsonHandling.loadJSON(buffername)
    embed=Embed(title=embedTitle)
    embed.add_field(name="Note",value=embedMessage,inline=False)
    for k,v in testBuffer.items():
        embed.add_field(name=k, value=v, inline=False)  
    return embed

def removeBuffer(serverName, bufferType, bufferNo:int):
    buffername = "buffers/" + serverName + bufferType +  ".json"    
    testBuffer = jsonHandling.loadJSON(buffername)   
    if bufferNo == 0:
        for x in list(testBuffer):
            del testBuffer[x]
    else:
        del testBuffer[bufferNo]
    jsonHandling.dumpJSON(buffername,testBuffer)
    return

def getAllBufferData(serverName, bufferType):
    buffername = "buffers/" + serverName + bufferType +  ".json"
    bufferData = jsonHandling.loadJSON(buffername)
    return bufferData

def getBufferData(serverName, bufferType, bufferNo:int):
    buffername = "buffers/" + serverName + bufferType +  ".json"    
    if os.path.exists(buffername):
        testBuffer = jsonHandling.loadJSON(buffername)
    else: 
        testBuffer = {}   
    return testBuffer[bufferNo]

def getBufferIDs(serverName, bufferType):
    buffername = "buffers/" + serverName + bufferType +  ".json"    
    if os.path.exists(buffername):
        testBuffer = jsonHandling.loadJSON(buffername)
    else: 
        testBuffer = {}   
    return list(testBuffer)

