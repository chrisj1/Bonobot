import sys

import numpy as np
import cv2

# reads in the image
image = cv2.imread(sys.argv[1], flags=cv2.IMREAD_COLOR)

def fry(image, saturation):
    # sets the green channel equal to the 
    # increase saturation
    hsvImg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    hsvImg[...,1] = hsvImg[...,1]*saturation
    image=cv2.cvtColor(hsvImg,cv2.COLOR_HSV2BGR)
    
    image[...,0] = image[...,0] * 1.1 # sets the red channel to the green channel
    image[...,1] = image[...,0] * 1.1 # sets the red channel to the green channel
    return image

def sharp(image):
    # sharpening kernel
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    return cv2.filter2D(src=image, ddepth=-1, kernel=kernel)

cv2.imwrite("fry.png", fry(image, 1.4))
cv2.imwrite("output.png", fry(sharp(sharp(image)), 5))
