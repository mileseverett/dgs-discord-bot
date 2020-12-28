import os
import json
import requests
import sys
import traceback
import mysql.connector

import cv2 
import io
import numpy as np
import difflib
import imutils

import mimetypes, urllib
from PIL import Image, ImageEnhance, ImageFilter, ImageChops

import discord
from discord.ext import commands

from utils import jsonHandling
from utils.misc import createFolder

class winterfaceReader(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.activeMessages = []

    def uploadToDB(self, playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime):
        # Connect to DB
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        host = os.getenv('MYSQL_HOST')
        port = os.getenv('MYSQL_PORT')

        conn = mysql.connector.connect(user=user
                              , password=password
                              ,host=host
                              ,port=port
                              ,database='DGS_Hiscores')

        query_string = "INSERT INTO submission_raw (playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(playerOne, playerTwo, playerThree, playerFour, playerFive, theme, endTime)
        try:
            cursor = conn.cursor()
            cursor.execute(query_string)
            floorID = cursor.lastrowid
            cursor.close()
            
            cursor = conn.cursor()
            cursor.execute("INSERT INTO submission_status (floorID, completedInd) values ({}, 0)".format(floorID))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return True
    
    @commands.command(name="highscore")
    async def highscore(self, ctx, url):
        try:
            print (url)
            isValid = (self.is_url_image(url))
            if isValid == True:
                r = requests.get(url)
                image = Image.open(io.BytesIO(r.content))
                image.save("image.png")
                img = cv2.imread("image.png",0)
                # print (img)
                # top_left,bottom_right = self.findWinterface(img)
                # top_left,bottom_right = self.findWinterface2()
                top_left,bottom_right = self.findWinterface3()
                # self.findArrows()

                print (top_left,bottom_right)
                
                image = image.crop((top_left[0],top_left[1],bottom_right[0],bottom_right[1]))
                image = image.resize((512,334))
                # print (image.getpixel((0,0)))
                image.save("hmm.png")
                counter = 1
                coordinates = {
                    1:{"name":"rect","x":361,"y":36,"width":110,"height":19},
                    2:{"name":"rect","x":361,"y":86,"width":110,"height":19},
                    3:{"name":"rect","x":361,"y":136,"width":110,"height":19},
                    4:{"name":"rect","x":361,"y":186,"width":110,"height":19},
                    5:{"name":"rect","x":361,"y":236,"width":110,"height":19}
                } 

                # nonNamesCoordinates = {
                #     "time":{"name":"rect","x":32,"y":306,"width":47,"height":12},
                #     "floor":{"name":"rect","x":44,"y":54,"width":54,"height":15},
                #     "level-mod":{"name":"rect","x":298,"y":158,"width":33,"height":17},
                #     "bonus":{"name":"rect","x":300,"y":138,"width":31,"height":16}
                # }

                nonNamesCoordinates = {
                    "time":{"name":"rect","x":32,"y":306,"width":47,"height":12}
                }

                themeCoordinates = {
                    "floor":{"name":"rect","x":44,"y":54,"width":54,"height":15}
                }

                (width,height) = image.width, image.height
                # print (width)
                # print (height)

                for k,v in coordinates.items():
                    im = image.crop((v["x"], v["y"], v["x"] + v["width"], v["y"] + v["height"]))
                    fname = "character/" + str(counter) + str(k) + ".png"
                    im.save(fname)

                for k,v in nonNamesCoordinates.items():
                    im = image.crop((v["x"], v["y"], v["x"] + v["width"], v["y"] + v["height"]))
                    fname = "times/" + str(counter) + str(k) + ".png"
                    im.save(fname)

                for k,v in themeCoordinates.items():
                    im = image.crop((v["x"], v["y"], v["x"] + v["width"], v["y"] + v["height"]))
                    fname = "floor/" + str(counter) + str(k) + ".png"
                    im.save(fname)

                names = self.findNames(ctx)
                print(names)
                str(names)
                time = self.findTime(ctx)
                theme = self.findTheme(ctx)
                print(time)

                # upload data to DB
                # self.uploadToDB(playerOne = names[0], playerTwo = names[1], playerThree = names[2], playerFour = names[3], playerFive = names[4], theme = 'Frozen', endTime = time) # frozen hard coded for now

                embed = self.generateEmbed(names,time,theme)
                message = await ctx.send(embed=embed)
                await message.add_reaction("\U00002705")
                await message.add_reaction("\U0000274C")
                self.activeMessages.append(message.id)
                print (self.activeMessages)
                
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)

    def generateEmbed(self,names,time,theme):
        embed = discord.Embed(title="Winterface Data")
        counter = 1
        for x in names:
            embed.add_field(name="Player " + str(counter), value=x, inline=False)
            counter = counter + 1
        embed.add_field(name="Time",value=time,inline=False)
        embed.add_field(name="Theme",value=theme,inline=False)
        return embed

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

    def findWinterface3(self):
        template = cv2.imread('winterfaces/winterface3.png')
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        # load the image, convert it to grayscale, and initialize the
        # bookkeeping variable to keep track of the matched region
        image = cv2.imread('image.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found = None

        # loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break
            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # draw a bounding box around the detected region
            clone = np.dstack([edged, edged, edged])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            # cv2.imshow("Visualize", clone)
            # cv2.waitKey(0)

            # if we have found a new maximum correlation value, then update
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

        # draw a bounding box around the detected result and display the image
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.imwrite("hmm2.png",image)
        return (startX, startY), (endX, endY)

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
        # img = self.unsharp_mask(img)
        # img2 = img.copy()
        template = cv2.imread('winterfaces/winterface2.png',0)
        # template = self.unsharp_mask(template)
        w, h = template.shape[::-1]
        template = self.image_resize(template,width=w*2,height=h*2)
        # All the 6 methods for comparison in a list
        # methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,
        #             cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]
        # for method in methods:
        # img = img2.copy()
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
        print (top_left,bottom_right)
        return top_left,bottom_right

    def image_resize(self, image, width = None, height = None, inter = cv2.INTER_AREA):
        # initialize the dimensions of the image to be resized and
        # grab the image size
        dim = None
        (h, w) = image.shape[:2]

        # if both the width and height are None, then return the
        # original image
        if width is None and height is None:
            return image

        # check to see if the width is None
        if width is None:
            # calculate the ratio of the height and construct the
            # dimensions
            r = height / float(h)
            dim = (int(w * r), height)

        # otherwise, the height is None
        else:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))

        # resize the image
        resized = cv2.resize(image, dim, interpolation = inter)

        # return the resized image
        return resized

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

    def findTheme(self,ctx):
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
            print (fullTime)
            timeDictList = (sorted(fullTime))
            print ("timeDictList",timeDictList)
            timeStr = ""
            for x in timeDictList:
                timeStr = timeStr + str(fullTime[x]["character"])
            return int(timeStr)

        def findNonZeros(filepath,fullTime,glwidth,glheight,k):
            zero = Image.open(filepath)
            zero = zero.convert('1')
            (glwidth,glheight) = zero.width, zero.height
            for x in range(0,twidth - glwidth + 1):
                im = time.crop((x, rowY, x + glwidth, rowY + glheight))
                if fuzzyEqual(im,zero) < 0.05:
                    charDict= {"character":k,"charLength":glwidth}
                    fullTime[x] = charDict
            return fullTime


        floorChars = {
            1:"floorGlyph/floor1.png",
            2:"floorGlyph/floor2.png",
            3:"floorGlyph/floor3.png",
            4:"floorGlyph/floor4.png",
            5:"floorGlyph/floor5.png",
            6:"floorGlyph/floor6.png",
            7:"floorGlyph/floor7.png",
            8:"floorGlyph/floor8.png",
            9:"floorGlyph/floor9.png",
            0:"floorGlyph/floor0.png"
        }    

        times = []
        for file in os.listdir("./floor"):
            times.append(file)

        print (times)

        for t in times:
            fullTime = {}
            fname = "floor/" + t
            print (fname)
            time = Image.open(fname)
            zero = Image.open("glypths/time0.png")
            
            datas = time.getdata()

            new_image_data = []
            for item in datas:
                # change all white (also shades of whites) pixels to yellow
                if item[0] == 160:
                    new_image_data.append((198, 155, 1))
                else:
                    new_image_data.append(item)
            
            time.putdata(new_image_data)

            enhancer = ImageEnhance.Contrast(time)
            time = enhancer.enhance(2)

            (glwidth,glheight) = zero.width, zero.height
            (twidth,theight) = time.width, time.height

            # print (twidth,theight)

            time = time.convert('1')
            time.save("ahh/" + t + "test.png")
            # rowX,rowY = (findRow(zero,time))
            
            foundChar = "Not Found"
            matchFound = False
            for k,v in floorChars.items():
                # print ("trying:",k)
                zero = Image.open(v)
                zero = zero.convert('1')
                matchFound,rowX,rowY = (findRow(zero,time,k))
                if matchFound == True:
                    fullTime[rowX] = k
                    break

            print (matchFound,rowX,rowY,fullTime)

            # if rowX == 0:
            #     print ("Couldn't find time")
            #     continue

            # for x in range(rowX + 1,twidth - glwidth + 1):
            #     im = time.crop((x, rowY, x + glwidth, rowY + glheight))
            #     if equal(im,zero):
            #         fullTime[x] = 0

            # breakAt = 0
            for k,v in floorChars.items():
                fullTime = findNonZeros(v,fullTime,glwidth,glheight,k)
                # print (fullTime)
            decoded = (decoder(fullTime))
            if decoded in range(0,12):
                return "Frozen"
            elif decoded in range(12,18):
                return "Abandoned 1"
            elif decoded in range(18,30):
                return "Furnished"
            elif decoded in range(30,36):
                return "Abandoned 2"
            elif decoded in range(36,48):
                return "Occult"
            elif decoded in range(48,61):
                return "Warped"



    def findTime(self,ctx):
        def equal(im1, im2):
            return ImageChops.difference(im1, im2).getbbox() is None

        def fuzzyEqual(im1,im2):
            im1 = np.array(im1)
            im2 = np.array(im2)
            err = np.sum((im1.astype("float") - im2.astype("float")) ** 2)
            err /= float(im1.shape[0] * im1.shape[1])
            return err 

        def findRow(zero,time):
            (glwidth,glheight) = zero.width, zero.height
            (twidth,theight) = time.width, time.height
            for x in range(twidth - glwidth):
                for y in range(theight - glheight ):
                    im = time.crop((x, y, x + glwidth, y + glheight))
                    # im.save("test/" + str(x) + " " + str(y) +".png")
                    # if equal(im,zero):
                    # print (fuzzyEqual(im,zero))
                    
                    if fuzzyEqual(im,zero) < 0.10:
                        # print ("match found")
                        # print (fuzzyEqual(im,zero))
                        fullTime[x] = 0
                        mainX = x
                        mainY = y
                        im.save("test/" + str(x) + " " + str(y) + ".png")
                        return mainX, mainY
            mainX = 0
            mainY = 0
            return mainX, mainY

        def decoder(fullTime):
            print (fullTime)
            timeDictList = (sorted(fullTime))
            timeStr = ""
            for x in timeDictList:
                timeStr = timeStr + str(fullTime[x])
            return timeStr

        def findNonZeros(filepath,fullTime,glwidth,glheight,k):
            zero = Image.open(filepath)
            (glwidth,glheight) = zero.width, zero.height
            for x in range(twidth - glwidth + 1):
                im = time.crop((x, rowY, x + glwidth, rowY + glheight))
                # im.save("testRowOther/" + str(x) + " " + str(rowY) + ".png")
                if equal(im,zero):
                    fullTime[x] = k
                    # breakAt = x + glwidth
            return fullTime


        nonZeros = {
            1:"glypths/time1.png",
            2:"glypths/time2.png",
            3:"glypths/time3.png",
            4:"glypths/time4.png",
            5:"glypths/time5.png",
            6:"glypths/time6.png",
            7:"glypths/time7.png",
            8:"glypths/time8.png",
            9:"glypths/time9.png"
        }    

        times = []
        for file in os.listdir("./times"):
            times.append(file)

        print (times)

        for t in times:
            fullTime = {}
            fname = "times/" + t
            print (fname)
            time = Image.open(fname)
            zero = Image.open("glypths/time0.png")

            enhancer = ImageEnhance.Contrast(time)
            time = enhancer.enhance(2)

            (glwidth,glheight) = zero.width, zero.height
            (twidth,theight) = time.width, time.height

            # print (twidth,theight)

            time = time.convert('1')
            time.save("ahh/" + t + "test.png")
            rowX,rowY = (findRow(zero,time))
            
            if rowX == 0:
                print ("Couldn't find time")
                continue

            for x in range(rowX + 1,twidth - glwidth + 1):
                im = time.crop((x, rowY, x + glwidth, rowY + glheight))
                if equal(im,zero):
                    fullTime[x] = 0

            breakAt = 0
            for k,v in nonZeros.items():
                fullTime = findNonZeros(v,fullTime,glwidth,glheight,k)

            return (decoder(fullTime))


    def findNames(self,ctx):
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

        namesFound = []

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
                # namesDict[name] = None
                jsonHandling.dumpJSON(fname,namesDict)
                print ("name=====",name)
                namesFound.append(name)
            else:
                namesFound.append("None")
        return namesFound

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.message_id in self.activeMessages and payload.user_id != 722758078310776832 and payload.user_id != 718483095262855280:
            print ("accepted or declined")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')
    


def setup(bot):
    bot.add_cog(winterfaceReader(bot))