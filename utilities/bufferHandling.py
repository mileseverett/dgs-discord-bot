import os
import random
import string
import json
import sys, traceback

from discord import Embed
from utilities import jsonHandling

def addBuffer(serverName, bufferType, data):
    """
        Helper function to add arbitrary data to the buffer you specify. Assigns a unique ID for the data within that buffer

        Parameters:
        bufferType - string name of the buffer to add to: for example, "vouches"
        data - data to add to the buffer
    """
    # generate filename of settings file
    settingsFileName = "guildsettings/" + serverName + ".json"

    # load settings info
    if os.path.exists(settingsFileName):
        settings = jsonHandling.loadJSON(settingsFileName)
    else: 
        settings = {}

    # determine which ID to grab
    IDType = bufferType + "IDcounter"

    # get unique ID of new buffer item
    try: 
        ID = settings[IDType]
        settings[IDType] = settings[IDType] + 1
    except Exception as e:
        print (e)
        ID = 1
        settings[IDType] = ID + 1

    # update settings file
    jsonHandling.dumpJSON(settingsFileName, settings)

    # generate filename of buffer file for this server + buffer type
    buffername = "buffers/" + serverName + bufferType + ".json"    
    print ("buffername", buffername)
    # load buffer
    if os.path.exists(buffername):
        testBuffer = jsonHandling.loadJSON(buffername)
    else: 
        testBuffer = {}    

    # add data to the buffer at correct ID
    testBuffer[ID] = data

    # save the buffer data
    jsonHandling.dumpJSON(buffername, testBuffer)
    return

def viewBuffer(serverName, bufferType, embedTitle, embedMessage):
    """
        Helper function to view a buffer

        Parameters:
        bufferType - string name of the buffer to view: for example, "vouches"
    """
    buffername = "buffers/" + serverName + bufferType +  ".json"    
    testBuffer = jsonHandling.loadJSON(buffername)
    embed=Embed(title=embedTitle)
    embed.add_field(name="Note",value=embedMessage,inline=False)
    for k,v in testBuffer.items():
        embed.add_field(name=k, value=v, inline=False)  
    return embed

def removeBuffer(serverName, bufferType, bufferNo:int):
    """
        Helper function to remove an entry from a buffer

        Parameters:
        bufferType - string name of the buffer to view: for example, "vouches"
        bufferNo - integer ID of the buffer entry to delete
    """
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
    """
        Helper function to get all data from a specific buffer

        Parameters:
        bufferType - string name of the buffer to view: for example, "vouches"
    """
    buffername = "buffers/" + serverName + bufferType +  ".json"
    bufferData = jsonHandling.loadJSON(buffername)
    return bufferData

def getBufferData(serverName, bufferType, bufferNo:int):
    """
        Helper function to get a specific entry from a specified buffer

        Parameters:
        bufferType - string name of the buffer to view: for example, "vouches"
        bufferNo - integer ID of the buffer entry to delete
    """
    buffername = "buffers/" + serverName + bufferType +  ".json"    
    if os.path.exists(buffername):
        testBuffer = jsonHandling.loadJSON(buffername)
    else: 
        testBuffer = {}   
    return testBuffer[bufferNo]

def getBufferIDs(serverName, bufferType):
    """
        Helper function to get a list of all IDs in a buffer

        Parameters:
        bufferType - string name of the buffer to view: for example, "vouches"
    """
    buffername = "buffers/" + serverName + bufferType +  ".json"    
    if os.path.exists(buffername):
        testBuffer = jsonHandling.loadJSON(buffername)
    else: 
        testBuffer = {}   
    return list(testBuffer)

