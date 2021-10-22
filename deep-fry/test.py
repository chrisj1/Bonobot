import sys

import numpy as np
import cv2

# reads in the image
image = cv2.imread(sys.argv[1], flags=cv2.IMREAD_COLOR)

def fry(image):
    # sets the green channel equal to the 
    # increase saturation
    image[:,:,1] = image[:,:,0] # sets the red channel to the green channel
    return image

def sharp(image):
    # sharpening kernel
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    return cv2.filter2D(src=image, ddepth=-1, kernel=kernel)

# cv2.imwrite("fry.png", fry(image))
cv2.imwrite("output.png", sharp(sharp(sharp(fry(image)))))

