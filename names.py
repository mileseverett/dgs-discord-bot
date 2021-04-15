import os
import random
import pickle
import string
import json
import requests
import sys
import traceback
import urllib.request
import discord
from discord.ext import commands
import mimetypes, urllib
from PIL import Image, ImageEnhance, ImageFilter, ImageChops
import cv2 
import io
import numpy as np
import difflib
import imutils
from utils import jsonHandling
from utils.misc import createFolder
def equal(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None

def fuzzyEqual(im1,im2):
    im1 = np.array(im1)
    im2 = np.array(im2)
    err = np.sum((im1.astype("float") - im2.astype("float")) ** 2)
    err /= float(im1.shape[0] * im1.shape[1])
    return err 

def findRow(zero,time,charName):
    (glwidth,glheight) = zero.width, zero.height
    (twidth,theight) = time.width, time.height
    for x in range(twidth - glwidth):
        for y in range(theight - glheight ):
            im = time.crop((x, y, x + glwidth, y + glheight))
            # im.save("test/" + str(x) + " " + str(y) +".png")
            # if equal(im,zero):
            # print (fuzzyEqual(im,zero))
            
            if fuzzyEqual(im,zero) < 0.05:
                print ("match found at ",x,y)
                print (fuzzyEqual(im,zero))
                charDict= {"character":charName,"charLength":glwidth}
                fullTime[x] = charDict
                mainX = x
                mainY = y
                im.save("test/" + str(x) + " " + str(y) + ".png")
                return True,mainX, mainY
    mainX = 0
    mainY = 0
    return False,mainX, mainY

def decoder(fullTime):
    timeDictList = (sorted(fullTime))
    timeStr = ""
    prevX = 0
    # print (fullTime)
    # print (timeDictList)
    for x in timeDictList:
        # print (prevX)
        # print (fullTime[x])
        # print ("diff:",x - prevX)
        if (x - prevX > 3 and prevX > 0):
            timeStr = timeStr + " " + str(fullTime[x]["character"])
        elif x-prevX < 0:
            continue
        else:
            timeStr = timeStr + str(fullTime[x]["character"])
        prevX = int(x) + int(fullTime[x]["charLength"])
    return timeStr

def findNonZeros(filepath,fullTime,glwidth,glheight,k):
    # print (filepath)
    zero = Image.open(filepath)
    zero = zero.convert('1')
    (glwidth,glheight) = zero.width, zero.height
    for x in range(0,twidth - glwidth + 1):
        # print ((x, rowY, x + glwidth, rowY + glheight))
        im = time.crop((x, rowY, x + glwidth, rowY + glheight))
        # im.save("testRowOther/" + str(x) + " " + str(rowY) + ".png")
        if fuzzyEqual(im,zero) < 0.05:
            charDict= {"character":k,"charLength":glwidth}
            fullTime[x] = charDict
    return fullTime

chars = {
    "u":"charGlyph/glyphLowerU.png",
    "n":"charGlyph/glyphLowerN.png",
    "t":"charGlyph/glyphLowerT.png",
    "e":"charGlyph/glyphLowerE.png",
    "r":"charGlyph/glyphLowerR.png",
    "d":"charGlyph/glyphLowerD.png",
    "x":"charGlyph/glyphLowerX.png",
    "p":"charGlyph/glyphLowerP.png",
    "a":"charGlyph/glyphLowerA.png",
    "l":"charGlyph/glyphLowerL.png",
    "i":"charGlyph/glyphLowerI.png",
    "o":"charGlyph/glyphLowerO.png",
    "s":"charGlyph/glyphLowerS.png",
    "f":"charGlyph/glyphLowerF.png",
    "m":"charGlyph/glyphLowerM.png",
    "k":"charGlyph/glyphLowerK.png",
    "g":"charGlyph/glyphLowerG.png",
    "y":"charGlyph/glyphLowerY.png",
    "w":"charGlyph/glyphLowerW.png",
    "h":"charGlyph/glyphLowerH.png",
    "b":"charGlyph/glyphLowerB.png",
    "c":"charGlyph/glyphLowerC.png",
    "q":"charGlyph/glyphLowerQ.png",
    "z":"charGlyph/glyphLowerZ.png",
    "v":"charGlyph/glyphLowerV.png",
    "j":"charGlyph/glyphLowerJ.png",
    "H":"charGlyph/glyphCapH.png",
    "Q":"charGlyph/glyphCapQ.png",
    "C":"charGlyph/glyphCapC.png",
    "D":"charGlyph/glyphCapD.png",
    "S":"charGlyph/glyphCapS.png",
    "G":"charGlyph/glyphCapG.png",
    "O":"charGlyph/glyphCapO.png",
    "E":"charGlyph/glyphCapE.png",
    "T":"charGlyph/glyphCapT.png",
    "Y":"charGlyph/glyphCapY.png",
    "K":"charGlyph/glyphCapK.png",
    "B":"charGlyph/glyphCapB.png",
    "F":"charGlyph/glyphCapF.png",
    "M":"charGlyph/glyphCapM.png",
    "I":"charGlyph/glyphCapI.png",
    "U":"charGlyph/glyphCapU.png",
    "R":"charGlyph/glyphCapR.png",
    "P":"charGlyph/glyphCapP.png",
    "X":"charGlyph/glyphCapX.png",
    "W":"charGlyph/glyphCapW.png",
    "V":"charGlyph/glyphCapV.png",
    "Z":"charGlyph/glyphCapZ.png",
    "A":"charGlyph/glyphCapA.png",
    "L":"charGlyph/glyphCapL.png",
    "M":"charGlyph/glyphCapM.png",
    "N":"charGlyph/glyphCapN.png",
    "P":"charGlyph/glyphCapP.png",
    "J":"charGlyph/glyphCapJ.png",
    "1":"charGlyph/glyphName1.png",
    "2":"charGlyph/glyphName2.png",
    "3":"charGlyph/glyphName3.png",
    "4":"charGlyph/glyphName4.png",
    "5":"charGlyph/glyphName5.png",
    "6":"charGlyph/glyphName6.png",
    "7":"charGlyph/glyphName7.png",
    "8":"charGlyph/glyphName8.png",
    "9":"charGlyph/glyphName9.png",
    "0":"charGlyph/glyphName0.png"
}    

times = []
for file in os.listdir("./character"):
    times.append(file)

for t in times:
    name = "Couldn't find name"
    fullTime = {}
    fname = "character/" + t
    # print (fname)
    time = Image.open(fname)
    rows,cols = time.size
    # print ("look here",rows,cols)
    # time = time.resize([rows*10,cols*10], Image.ANTIALIAS)
    # time.save("bigboy.png")
    enhancer = ImageEnhance.Contrast(time)
    time = enhancer.enhance(2)
    


    (twidth,theight) = time.width, time.height

    print (twidth,theight)

    time = time.convert('1')
    
    
    # time.save("processed.png")
    
    rows,cols = time.size
    print ("look here",rows,cols)
    for i in range(1,rows-1):
        for j in range(1,cols-1):
            amt = (time.getpixel((i-1,j)) + time.getpixel((i+1,j)) + time.getpixel((i,j-1)) + time.getpixel((i,j+1)) + time.getpixel((i+1,j-1)) + time.getpixel((i+1,j+1)) + time.getpixel((i-1,j-1)) + time.getpixel((i,j+1)))
            if amt == 0:
                time.putpixel((i,j),0)

    # time.save("ahh/" + t + "test.png")
    time = Image.open("ahh/" + t + "test.png")
    matchFound = False
    for k,v in chars.items():
        # print ("trying:",k)
        zero = Image.open(v)
        # print (v)
        # rows0,cols0 = zero.size
        # zero = zero.resize([rows0*10,cols0*10], Image.ANTIALIAS)
        zero = zero.convert('1')
        matchFound,rowX,rowY = (findRow(zero,time,k))
        if matchFound == True:
            break

    (glwidth,glheight) = zero.width, zero.height

    if rowX == 0:
        print ("Couldn't find name")

    for x in range(rowX + 1,twidth - glwidth + 1):
        im = time.crop((x, rowY, x + glwidth, rowY + glheight))
        if fuzzyEqual(im,zero) < 0.05:
            fullTime[x] = 0

    for k,v in chars.items():
        fullTime = findNonZeros(v,fullTime,glwidth,glheight,k)

    print (fullTime)
    print (decoder(fullTime))
    name = decoder(fullTime)
    fname = "names/names.json"
    namesDict = jsonHandling.loadJSON(fname)
    possibleDgers = list(namesDict.keys())

    if name in possibleDgers:
        print (fname[:-4],name)
    elif name is None:
        print (fname[:-4],"NA")
        continue
    else:
        closestMatch = difflib.get_close_matches(name,possibleDgers)
        if len(closestMatch) > 0:
            print (fname[:-4],closestMatch[0])
            name = closestMatch[0]
        else:
            print (fname[:-4],"NA")

    if name == None: 
        name = "None found"
    elif len(name) > 0:
        namesDict[name] = None
        jsonHandling.dumpJSON(fname,namesDict)
        print ("name=====",name)
        print(name)
    else:
        print("No name found")