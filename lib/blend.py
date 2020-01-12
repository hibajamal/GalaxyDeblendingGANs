import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from PIL import Image

'''
img1 = cv2.imread("img1.jpg")
img2 = cv2.imread("img2.jpg")

# create new img//wider
new_width = img1.shape[0] + 30
blended = np.zeros((new_width, img1.shape[1], img1.shape[2]))

# put in img1
for i in range(img1.shape[0]):
    for j in range(img1.shape[1]):
        blended[i, j] = img1[i, j]

cv2.imshow("img1", blended)
#cv2.imshow("img2",img2)

cv2.waitKey()
'''
img1 = Image.open("images/img1.jpg")
img2 = Image.open("images/img2.jpg")

img1 = img1.convert('RGB')
img2 = img2.convert('RGB')

new_width = img1.size[0] + 80
blended = Image.new(img1.mode, (new_width, img1.size[1]))
blended_p = blended.load()
img1_p = img1.load()
img2_p = img2.load()

for i in range(blended.size[0]):
    for j in range(blended.size[1]):
        # get instensity
        if i < 80:
            blended_p[i, j] = img1_p[i, j]
        else:
            R1, B1, G1 = -1, -1, -1
            if (i < img1.size[0]):
                R1, B1, G1 = img1.getpixel((i, j))
            R2, B2, G2 = img2.getpixel((i-80, j))
            intensity2 = sum([R2, G2, B2]) / 3
            intensity1 = sum([R1, G1, B1]) / 3
            if (intensity1 > intensity2):
                blended_p[i, j] = img1_p[i, j]
            else:
                blended_p[i, j] = img2_p[i-80, j]

img1.show()
img2.show()
blended.show()