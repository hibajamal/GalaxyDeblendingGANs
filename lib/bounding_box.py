import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImagePath
import math
import xlsxwriter
import sys
import os

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
    if point[0] - x <= 0:
        x += point[0] - x
    if point[0] + x >= img.size[0]:
        x -= (point[0] + x) - (img.size[0] - 1)
    if point[1] - y <= 0:
        y += point[1] - y
    if point[1] + y >= img.size[1]:
        y -= (point[1] + y) - (img.size[1] - 1)
    # start checking from new block
    new_point = (point[0]-x//2, point[1]+y//2)
    for i in range(math.ceil(new_point[0]), math.ceil(new_point[0]+x)):
        for j in range(math.ceil(new_point[1]), math.ceil(new_point[1]+y)):
            if i < img.size[0] and j < img.size[1]:
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
        if INTENSITY_CMP[0] - region > 50:
            return INTENSITY_CMP[1]
        INTENSITY_CMP[1] = (x, y)
        INTENSITY_CMP[0] = region
        if THRESHBlock((x, y), img):
            return x, y
    return 0, 0

directory = 'images_training_rev1'
workbook = xlsxwriter.Workbook('labels.xlsx')
worksheet = workbook.add_worksheet()
cell_format = workbook.add_format()
cell_format.set_bold()
cell_format = workbook.add_format({'bold': True})
row = 0
worksheet.write(row, 0, 'Name', cell_format)
worksheet.write(row, 1, 'x1', cell_format)
worksheet.write(row, 2, 'y1', cell_format)
worksheet.write(row, 3, 'x2', cell_format)
worksheet.write(row, 4, 'y2', cell_format)

for filename in os.listdir(directory):
    img = Image.open(directory+'/'+filename)
    img = img.convert('RGB')
    img_array = img.load()

    img1 = ImageDraw.Draw(img)
    point = (212, 212)
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
    #Getting the top left corner of Rect
    topLeft = [min(thirty_[9][0], thirty_[-2][0], thirty_[-1][0]), min(thirty_[0][1],
                    thirty_[-2][1], thirty_[-1][1])]
    bottomLeft = [min(thirty_[9][0], thirty_[8][0], thirty_[7][0]), max(thirty_[6][1],
                    thirty_[8][1], thirty_[7][1])]
    topRight = [max(thirty_[3][0], thirty_[1][0], thirty_[2][0]), min(thirty_[0][1],
                    thirty_[1][1], thirty_[2][1])]
    bottomRight = [max(thirty_[3][0], thirty_[5][0], thirty_[4][0]), max(thirty_[6][1],
                    thirty_[4][1], thirty_[5][1])]
    topLeft[0] = bottomLeft[0] = min(topLeft[0], bottomLeft[0])
    topLeft[1] = topRight[1] = min(topLeft[1], topRight[1])
    bottomLeft[1] = bottomRight[1] = max(bottomLeft[1], bottomRight[1])
    topRight[0] = bottomRight[0] = max(topRight[0], bottomRight[0])
    b_rect = [tuple(topLeft), tuple(topRight), tuple(bottomRight), tuple(bottomLeft)]
    print("Rect: ", b_rect, "done with:", filename)
    img1.polygon(b_rect, fill = None, outline = 'red')

    #check bounds
    if abs(topLeft[0] - topRight[0]) < 200 and abs(bottomLeft[0] - bottomRight[0] < 200) and abs(topLeft[1] - bottomLeft[1] < 200 and abs(topRight[1] - topLeft[1]) < 200):
        row += 1
        worksheet.write(row, 0, filename)
        worksheet.write(row, 1, b_rect[0][0])
        worksheet.write(row, 2, b_rect[0][1])
        worksheet.write(row, 3, b_rect[2][0])
        worksheet.write(row, 4, b_rect[2][1])
workbook.close()