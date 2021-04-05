# This code was adapted from the code here https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

import cv2
import sys
import re
import os

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False

rectangles = []


def click_and_crop(event, x, y, flags, param):
    global refPt, cropping, rectangles

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        x_size = abs(refPt[0][0] - refPt[1][0])
        y_size = abs(refPt[0][1] - refPt[1][1])
        min_size = 20
        if x_size < min_size or y_size < min_size:
            print(
                f"Rectangle is too small, both dementions must be > {min_size}px. You rectangle was {x_size}x{y_size}"
            )
            return

        # draw a rectangle around the region of interest
        cv2.rectangle(image, refPt[0], refPt[1], (0, 0, 255), 2)
        rectangles.append((refPt[0], refPt[1]))
        cv2.imshow("image", image)


if len(sys.argv) < 2:
    print("Usage: python generate.py <image>")
    print("Example: python generate.py ../autotemplates/template01.png")
    exit()

print("To use the program draw out a rectangle over the face of each bonobo")
print("If you make a mistake, press the 'r' key to reset the entire image")
print("Once all the bonobos have a face, press the 'enter' key to save and exit")
print("The 'esc' key can be used to exit the program without saving")

# load the image, clone it, and setup the mouse callback function
image = cv2.imread(sys.argv[1])
mask = image.copy()
copy = image.copy()
cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)


while True:
    # display the image and wait for a keypress
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF

    # 'r' key pressed means reset rectangles
    if key == ord("r"):
        image = copy.copy()
        rectangles = []
    # 'enter' key pressed means save mask
    # also works with the 'c' key just in case mac enter keys are a different value
    elif key == 13 or key == ord("c"):
        break
    # 'esc' key pressed means exit the program
    elif key == 27:
        exit()


# White out background
cv2.rectangle(mask, (0, 0), (mask.shape[1], mask.shape[0]), (255, 255, 255), -1)

for rect in rectangles:
    cv2.rectangle(mask, rect[0], rect[1], (0, 0, 0), -1)


path = re.sub(r"(^.*?)\.\w+?$", r"\1.png", sys.argv[1])
mask_path = re.sub(r"(^.*?)\.\w+?$", r"\1_mask.png", sys.argv[1])
print(f"Saved mask to: {mask_path}")
cv2.imwrite(mask_path, mask)
if path != sys.argv[1]:
    cv2.imwrite(path, copy)
    print("Converted image to png file and removed the old image")
    os.remove(sys.argv[1])

# close all open windows
cv2.destroyAllWindows()
