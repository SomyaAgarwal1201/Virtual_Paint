import cv2
import time
import handtrackingmodule as htm
import numpy as np
import os

overlayList = []  # list to store all the images

brushThickness = 25
eraserThickness = 100
drawColor = (255, 0, 255)  # setting purple color

xp, yp = 0, 0
new_size=(640,360)
imgCanvas = np.zeros((360, 640, 3), np.uint8)  # defining canvas
cv2.resize(imgCanvas,new_size)

# images in header folder
folderPath = "Header"
myList = os.listdir(folderPath)  # getting all the images used in code
# print(myList)
for imPath in myList:  # reading all the images from the folder
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)  # inserting images one by one in the overlayList
header = overlayList[0]  # storing 1st image
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width
cap.set(4, 360)  # height

detector = htm.handDetector(detectionCon=0.50, maxHands=1)  # making object

while True:

    # 1. Import image
    success, img = cap.read()
    img = cv2.flip(img, 1)  # for neglecting mirror inversion
    cv2.resize(img, new_size)


    # 2. Find Hand Landmarks
    img = detector.findHands(img)  # using functions fo connecting landmarks
    cv2.resize(img, new_size)

    print(img.shape)
    lmList, bbox = detector.findPosition(img,
                                         draw=False)  # using function to find specific landmark position,draw false means no circles on landmarks

    if len(lmList) != 0:
        # print(lmList)
        x1, y1 = lmList[8][1], lmList[8][2]  # tip of index finger
        x2, y2 = lmList[12][1], lmList[12][2]  # tip of middle finger

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)

        # 4. If Selection Mode - Two finger are up
        if fingers[1] and fingers[2]:
            xp, yp = 0, 0
            # print("Selection Mode")
            # checking for click
            if y1 < 72:
                if 120 < x1 < 256:  # if i m clicking at purple brush
                    header = overlayList[0]
                    drawColor = (255, 0, 255)
                elif 270 < x1 < 400:  # if i m clicking at blue brush
                    header = overlayList[1]
                    drawColor = (0,255,0)
                elif 420 < x1 < 550:  # if i m clicking at green brush
                    header = overlayList[2]
                    drawColor = (0, 0,255)
                elif 570 < x1 < 630:  # if i m clicking at eraser
                    header = overlayList[3]
                    drawColor = (0, 0, 0)
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor,
                          cv2.FILLED)  # selection mode is represented as rectangle

        # 5. If Drawing Mode - Index finger is up
        if fingers[1] and fingers[2] == False:
            cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)  # drawing mode is represented as circle
            # print("Drawing Mode")
            if xp == 0 and yp == 0:  # initially xp and yp will be at 0,0 so it will draw a line from 0,0 to whichever point our tip is at
                xp, yp = x1, y1  # so to avoid that we set xp=x1 and yp=y1
            # till now we are creating our drawing but it gets removed as everytime our frames are updating so we have to define our canvas where we can draw and show also

            # eraser
            if drawColor == (0, 0, 0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor,
                         brushThickness)  # gonna draw lines from previous coodinates to new positions
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
            xp, yp = x1, y1  # giving values to xp,yp everytime

        # merging two windows into one imgcanvas and img

    # 1 converting img to gray
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    cv2.resize(imgGray,new_size)

    # 2 converting into binary image and thn inverting
    _, imgInv = cv2.threshold(imgGray, 50, 255,
                              cv2.THRESH_BINARY_INV)  # on canvas all the region in which we drew is black and where it is black it is cosidered as white,it will create a mask
    cv2.resize(imgInv, new_size)

    imgInv = cv2.cvtColor(imgInv,
                          cv2.COLOR_GRAY2BGR)  # converting again to gray bcoz we have to add in a RGB image i.e img

    # add original img with imgInv ,by doing this we get our drawing only in black color
    cv2.resize(imgInv, new_size)


    img = cv2.bitwise_and(img, imgInv)
    cv2.resize(img, new_size)
    print(imgInv.shape)


    # add img and imgcanvas,by doing this we get colors on img
    img = cv2.bitwise_or(img, imgCanvas)
    cv2.resize(img, new_size)

    # setting the header image
    img[0:74, 0:640] = header  # on our frame we are setting our JPG image acc to H,W of jpg images

    cv2.imshow("Image", img)
    # cv2.imshow("Canvas", imgCanvas)
    # cv2.imshow("Inv", imgInv)
    cv2.waitKey(1)