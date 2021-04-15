import cv2
import numpy as np
import time
import pandas as pd 


image2 = cv2.imread('winterfaces/winterface3.png', cv2.IMREAD_COLOR)
image = cv2.imread('image.png', cv2.IMREAD_COLOR)
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
print (coords)
j = np.genfromtxt('colours.csv', delimiter=',')
# j2 = list(j)
# print (j2[0].dtype)
# all_rgb_codes = image2.reshape(-1, image.shape[-1])
# j = np.unique(all_rgb_codes, axis=0)
# print (j.dtype)

# for x in j.tolist():
#     print (x.dtype)


black = np.array([0,0,0])
print(black)

np.savetxt("colours.csv", j, delimiter=",")

print(np.unravel_index(sort[1], result.shape)) # second best match
print(np.unravel_index(sort[2], result.shape)) # best match
print(np.unravel_index(sort[3], result.shape)) # second best match
print(np.unravel_index(sort[4], result.shape)) # best match

#from arrow go right until you find either black (black space) or a colour which isn't in winterface (where winterface bg isn't black space)
for x in range(coords[1],width-1):
    if np.in1d(image[coords[0],x],j).any() and (image[coords[0],x] != black).all():
        pass
    else:
        endWinterfaceX = (coords[0],x-1)
        print ("end",endWinterfaceX)
        break


for y in range(coords[0],0,-1):
    if np.in1d(image[y,endWinterfaceX[1]],j).any() and (image[y,endWinterfaceX[1]] != black).all():
        pass
    else:
        startWinterfaceY = (y-1,endWinterfaceX[1])
        print ("start",startWinterfaceY)
        break

for x in range(endWinterfaceX,0,-1):
    if np.in1d(startWinterfaceY[0],x],j).any() and (startWinterfaceY[0],x] != black).all():
        pass
    else:
        startWinterfaceX = (startWinterfaceY[0],x)
        # print (startWinterfaceX)
        break

# for y in range(coords[0],height-1):
#     if np.in1d(image[y,coords[1]],j).any() and (image[y,coords[1]] != black).all():
#         pass
#     else:
#         endWinterfaceY = (y,coords[1])
#         # print (endWinterfaceY)
#         break




# print (startWinterfaceX[1]+1,startWinterfaceY[0]+1)
# print (endWinterfaceX[1]-1,endWinterfaceY[0]-1)