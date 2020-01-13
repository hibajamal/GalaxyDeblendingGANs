import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImagePath
import math
import sys

img = Image.open(str(sys.argv[-1]))
img = img.convert('RGB')
img_array = img.load()

intensity = lambda r, g, b: (r+g+b)/3
THRESHOLD = 37

def BrightSpot():
    HIGHEST = -math.inf
    point = (0, 0)
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            R, B, G = img.getpixel((i, j))
            if intensity(R, G, B) > HIGHEST:
                point = (i, j)
                HIGHEST = intensity(R, G, B)
    return point

def THRESHBlock(point, img):
    x, y = 10, 10
    # check if it goes out of range
    if point[0] - x < 0:
        x += point[0] - x
    if point[0] + x > img.size[0]:
        x -= (point[0] + x) - (img.size[0] - 1)
    if point[1] - y < 0:
        y += point[1] - y
    if point[1] + x > img.size[1]:
        y -= (point[1] + y) - (img.size[1] - 1)
    # start checking from new block
    new_point = (point[0]-x//2, point[1]+y//2)
    for i in range(math.ceil(new_point[0]), math.ceil(new_point[0]+x)):
        for j in range(math.ceil(new_point[1]), math.ceil(new_point[1]+y)):
            R, B, G = img.getpixel((i, j))
            if intensity(R, G, B) > THRESHOLD:
                return False
    return True

def RegionalIntensity(point, img, k=9):
    avg = 0
    count = 0
    for i in range(k):
        for j in range(k):
            if i+point[0] < img.size[0] and j+point[1] < img.size[1]:
                r, g, b = img.getpixel((point[0]+i, point[1]+j))
                avg += intensity(r, g, b)
                count+=1
    return avg/(k*k)

def LowerBound(point, img):
    for j in range(point[1], img.size[1]):
        if THRESHBlock((point[0], j), img):
            return point[1], j
    return 0, 0

def RightBound(point, img):
    for j in range(point[0], img.size[0]):
        if THRESHBlock((j, point[1]), img):
            return j, point[1]
    return 0, 0

def UpperBound(point, img):
    for j in range(point[1], -1, -1):
        if THRESHBlock((point[0], j), img):
            return point[0], j
    return 0, 0

def LeftBound(point, img):
    for j in range(point[0], -1, -1):
        if THRESHBlock((j, point[1]), img):
            return j, point[1]
    return 0, 0

def PolyBound(point, img, angle):
    m = math.tan(angle*(math.pi/180))
    print ("slope:", m)
    print ()
    y = point[1]
    x = point[0]
    INTENSITY_CMP = [RegionalIntensity(point, img), point]
    for i in range(1, 425):
        if 0 < angle < 90:
            y -= m
            x = point[0] + i
        elif 90 < angle < 180:
            y += (-1)*m
            x = point[0] + i
        elif 180 < angle < 270:
            y += m
            x = point[0] - i
        else:
            y -= (-1)*m
            x = point[0] - i
        region = RegionalIntensity((x, y), img, 10)
        print (INTENSITY_CMP, ",", abs(INTENSITY_CMP[0] - region))
        if INTENSITY_CMP[0] - region > 50:
            return INTENSITY_CMP[1]
        INTENSITY_CMP[1] = (x, y)
        INTENSITY_CMP[0] = region
        print (INTENSITY_CMP)
        if THRESHBlock((x, y), img):
            return x, y
    return 0, 0

# point = BrightSpot()
point = (212, 212)
print ("centre:", point)
# P1 = (LeftBound(point, img)[0], UpperBound(point, img)[1])
# P2 = (RightBound(point, img)[0], LowerBound(point, img)[1])

#print (point, point2)
img1 = ImageDraw.Draw(img)

#img1.rectangle([P1, P2], fill=None, outline="green")
'''lst = [LeftBound(point, img), PolyBound_x_270_to_0(point, img, (7*math.pi)/4), UpperBound(point, img), PolyBound_x_0_to_90(point, img, math.pi/4),
       RightBound(point, img), PolyBound_x_90_to_180(point, img, (3*math.pi)/4), LowerBound(point, img),
       PolyBound_x_180_to_270(point, img, (5*math.pi)/4)]
'''
thirty_ = [UpperBound(point, img),
           PolyBound(point, img, 60),
           PolyBound(point, img, 30),
           RightBound(point, img),
           PolyBound(point, img, 90+60),
           PolyBound(point, img, 90+30),
           LowerBound(point, img),
           PolyBound(point, img, 180+60),
           PolyBound(point, img, 180+30),
           LeftBound(point, img),
           PolyBound(point, img, 270+60),
           PolyBound(point, img, 270+30)]


img1.polygon(thirty_, fill=None, outline="green")
print("Thirty: ", thirty_)
#Getting the top left corner of Rect
topLeft = [min(thirty_[9][0],thirty_[-2][0],thirty_[-1][0]),min(thirty_[0][1],thirty_[-2][1],thirty_[-1][1])]
bottomLeft = [min(thirty_[9][0],thirty_[8][0],thirty_[7][0]), max(thirty_[6][1],thirty_[8][1],thirty_[7][1])]
topRight = [max(thirty_[3][0],thirty_[1][0],thirty_[2][0]) ,min(thirty_[0][1],thirty_[1][1],thirty_[2][1])]
bottomRight = [max(thirty_[3][0],thirty_[5][0],thirty_[4][0]), max(thirty_[6][1],thirty_[4][1],thirty_[5][1])]
topLeft[0] = bottomLeft[0] = min(topLeft[0],bottomLeft[0])
topLeft[1] = topRight[1] = min(topLeft[1],topRight[1])
bottomLeft[1] = bottomRight[1] = max(bottomLeft[1], bottomRight[1])
topRight[0] = bottomRight[0] = max(topRight[0],bottomRight[0])
rectBhai = [tuple(topLeft), tuple(topRight), tuple(bottomRight), tuple(bottomLeft)]
print("Rect: ", rectBhai)
img1.polygon(rectBhai, fill = None, outline = 'red')
print (RegionalIntensity(point, img))
r, g, b = img.getpixel((126, 346))
print ("bright intensity:", intensity(r, g, b))
r, g, b = img.getpixel((156, 288))
print ("mid intensity:", intensity(r, g, b))
r, g, b = img.getpixel((185, 279))
print ("border:", intensity(r, g, b))
img.show()


