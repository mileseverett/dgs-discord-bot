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



from utils import jsonHandling
from utils.misc import createFolder

class winterfaceReader(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="highscore")
    async def highscore(self, ctx, url):
        try:
            print (url)
            isValid = (self.is_url_image(url))
            if isValid == True:
                r = requests.get(url)
                image = Image.open(io.BytesIO(r.content))
                image.save("image.png")
                # img = cv2.imread("image.png",0)
                # print (img)
                # top_left,bottom_right = self.findWinterface(img)
                top_left,bottom_right = self.findWinterface2()
                # self.findArrows()

                print (top_left,bottom_right)
                
                image = image.crop((top_left[0],top_left[1],bottom_right[0],bottom_right[1]))
                image = image.resize((512,334))
                # print (image.getpixel((0,0)))
                image.save("hmm.png")
                # counter = 1
                # coordinates = {
                #     1:{"name":"rect","x":361,"y":36,"width":110,"height":19},
                #     2:{"name":"rect","x":361,"y":86,"width":110,"height":19},
                #     3:{"name":"rect","x":361,"y":136,"width":110,"height":19},
                #     4:{"name":"rect","x":361,"y":186,"width":110,"height":19},
                #     5:{"name":"rect","x":361,"y":236,"width":110,"height":19}
                # } 


                # (width,height) = image.width, image.height
                # # print (width)
                # # print (height)

                # for k,v in coordinates.items():

                #     im = image.crop((v["x"], v["y"], v["x"] + v["width"], v["y"] + v["height"]))
                #     fname = "character/" + str(counter) + str(k) + ".png"
                #     im.save(fname)
                # await self.findNames(ctx)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)

    def is_url_image(self,url):    
        mimetype,encoding = mimetypes.guess_type(url)
        return (mimetype and mimetype.startswith('image'))

    def check_url(self,url):
        """Returns True if the url returns a response code between 200-300,
        otherwise return False.
        """
        try:
            headers = {
                "Range": "bytes=0-10",
                "User-Agent": "MyTestAgent",
                "Accept": "*/*"
            }

            req = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(req)
            return response.code in range(200, 209)
        except Exception:
            return False

    def is_image_and_ready(self,url):
        return is_url_image(url) and check_url(url)
    
    def findArrows(self):
        
        img_rgb = cv2.imread('winterfaces/winterface2.png')
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread('winterfaces/arrows.png',0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where( res >= threshold)

        f = set()

        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

            sensitivity = 100
            f.add((round(pt[0]/sensitivity), round(pt[1]/sensitivity)))

        cv2.imwrite('res.png',img_rgb)

        found_count = len(f)
        print (found_count)

    def findWinterface2(self):
        image2 = cv2.imread('winterfaces/winterface3.png', cv2.IMREAD_COLOR)
        image = cv2.imread('winterfaces/bardy.png', cv2.IMREAD_COLOR)
        template = cv2.imread('winterfaces/arrows.png', cv2.IMREAD_COLOR)

        h, w = template.shape[:2]

        method = cv2.TM_CCOEFF_NORMED

        threshold = 0.95

        result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF)
        (min_x, max_y, minloc, maxloc) = cv2.minMaxLoc(result)
        (x,y) = minloc

        height,width = image.shape[:2]

        #get all the matches:
        result2 = np.reshape(result, result.shape[0]*result.shape[1])
        sort = np.argsort(result2)
        coords = np.unravel_index(sort[0], result.shape) # best match
    

        # all_rgb_codes = image2.reshape(-1, image.shape[-1])
        # j = np.unique(all_rgb_codes, axis=0)
        j = np.genfromtxt('colours.csv', delimiter=',',dtype="uint8")
        black = np.array([0,0,0])
        # print(black)

        for x in j.tolist():
            print (x)

        # print(np.unravel_index(sort[1], result.shape)) # second best match
        # print(np.unravel_index(sort[2], result.shape)) # best match
        # print(np.unravel_index(sort[3], result.shape)) # second best match
        # print(np.unravel_index(sort[4], result.shape)) # best match

        endWinterfaceX = (0,0)
        for x in range(coords[1],width-1):
            if np.in1d(image[coords[0],x],j).any() and (image[coords[0],x] != black).all():
            # if (image[coords[0],x] != black).all():
                pass
            else:
                endWinterfaceX = (coords[0],x)
                # print (endWinterfaceX)
                print (image[coords[0],x].dtype)
                break
        
        startWinterfaceX = (0,0)
        for x in range(coords[1],0,-1):
            if np.in1d(image[coords[0],x],j).any() and (image[coords[0],x] != black).all():
            # if (image[coords[0],x] != black).all():
                pass
            else:
                startWinterfaceX = (coords[0],x)
                # print (startWinterfaceX)
                print (image[coords[0],x])
                break

        endWinterfaceY = (0,0)
        for y in range(coords[0],height-1):
            if np.in1d(image[y,coords[1]],j).any() and (image[y,coords[1]] != black).all():
            # if (image[y,coords[1]] != black).all():
                pass
            else:
                endWinterfaceY = (y,coords[1])
                # print (endWinterfaceY)
                print (image[coords[0],x])
                break

        startWinterfaceY = (0,0)
        for y in range(coords[0],0,-1):
            if np.in1d(image[y,endWinterfaceX[1]],j).any() and (image[y,endWinterfaceX[1]] != black).all():
            # if (image[y,endWinterfaceX[1]] != black).all():
                pass
            else:
                startWinterfaceY = (y,coords[1])
                # print (startWinterfaceY)
                print (image[coords[0],x])
                break


        return (startWinterfaceX[1]+1,startWinterfaceY[0]+1),(endWinterfaceX[1]-1,endWinterfaceY[0]-1)

    def findWinterface(self,img):
        img = self.unsharp_mask(img)
        img2 = img.copy()
        template = cv2.imread('winterfaces/winterface2.png',0)
        w, h = template.shape[::-1]
        # All the 6 methods for comparison in a list
        # methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
        #             'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
        # for meth in methods:
        img = img2.copy()
        method = cv2.TM_CCOEFF
        # Apply template Matching
        res = cv2.matchTemplate(img,template,method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)


        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        return top_left,bottom_right

    def unsharp_mask(self, image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        """Return a sharpened version of the image, using an unsharp mask."""
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened

    async def findNames(self,ctx):
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
                        # print ("match found at ",x,y)
                        # print (fuzzyEqual(im,zero))
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

            enhancer = ImageEnhance.Contrast(time)
            time = enhancer.enhance(2)


            (twidth,theight) = time.width, time.height

            # print (twidth,theight)

            time = time.convert('1')
            
            
            
            
            rows,cols = time.size
            for i in range(1,rows-1):
                for j in range(1,cols-1):
                    amt = (time.getpixel((i-1,j)) + time.getpixel((i+1,j)) + time.getpixel((i,j-1)) + time.getpixel((i,j+1)) + time.getpixel((i+1,j-1)) + time.getpixel((i+1,j+1)) + time.getpixel((i-1,j-1)) + time.getpixel((i,j+1)))
                    if amt == 0:
                        time.putpixel((i,j),0)

            time.save("ahh/" + t + "test.png")
            matchFound = False
            for k,v in chars.items():
                # print ("trying:",k)
                zero = Image.open(v)
                zero = zero.convert('1')
                matchFound,rowX,rowY = (findRow(zero,time,k))
                if matchFound == True:
                    break

            (glwidth,glheight) = zero.width, zero.height

            if rowX == 0:
                print ("Couldn't find name")

            for x in range(rowX + 1,twidth - glwidth + 1):
                im = time.crop((x, rowY, x + glwidth, rowY + glheight))
                if equal(im,zero):
                    fullTime[x] = 0

            for k,v in chars.items():
                fullTime = findNonZeros(v,fullTime,glwidth,glheight,k)

            print (fullTime)
            print (decoder(fullTime))
            name = decoder(fullTime)
            fname = "names/" + ctx.guild.name.replace(" ","") + ".json"
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
                await ctx.send(name)
            else:
                await ctx.send("No name found")



    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')
    


def setup(bot):
    bot.add_cog(winterfaceReader(bot))