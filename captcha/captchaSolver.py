import random
import time
from ctypes import windll, Structure, c_long, byref, WINFUNCTYPE, c_bool, c_int, POINTER, create_unicode_buffer
import cv2
import numpy as np
from mss import mss
from pynput.mouse import Controller, Button
from captcha.utils import date
mouse = Controller()

#Windows functions
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

class RECT(Structure):
    _fields_ = [('left', c_long),
                ('top', c_long),
                ('right', c_long),
                ('bottom', c_long)]

enumWindows = windll.user32.EnumWindows
enumWindowsProc = WINFUNCTYPE(c_bool, c_int, POINTER(c_int))
getWindowText = windll.user32.GetWindowTextW
getWindowTextLength = windll.user32.GetWindowTextLengthW
isWindowVisible = windll.user32.IsWindowVisible
SW_RESTORE = 9
def _getAllTitles():
    titles = []
    def foreach_window(hWnd, lParam):
        if isWindowVisible(hWnd):
            length = getWindowTextLength(hWnd)
            buff = create_unicode_buffer(length + 1)
            getWindowText(hWnd, buff, length + 1)
            titles.append((hWnd, buff.value))
        return True
    enumWindows(enumWindowsProc(foreach_window), 0)

    return titles

def getWindowsWithTitle(title):
    hWndsAndTitles = _getAllTitles()
    windowObjs = []
    for hWnd, winTitle in hWndsAndTitles:
        if title.upper() in winTitle.upper():
            windowObjs.append(hWnd)
    return windowObjs

def getDimensions(window):
    r = RECT()
    res = windll.user32.GetWindowRect(window, byref(r))
    if res != 0:
        m = {
            'left': r.left,
            'top': r.top,
            'width': r.right - r.left,
            'height': r.bottom - r.top
        }
        return m

def getPointOnLine(x1, y1, x2, y2, n):
    x = ((x2 - x1) * n) + x1
    y = ((y2 - y1) * n) + y1
    return (x, y)

def linear(n):
    if not 0.0 <= n <= 1.0:
        raise Exception("Number not in range")
    return n

def getCursorPos():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return (pt.x, pt.y)
#End ctype functions


#Main Code
def locate(tmpName, img, confidence=0.85):
    array = locateAll(tmpName, img, confidence)
    if(len(array) > 0):
        return array[0]
    return None

def locateAll(tmpName, img, confidence=0.85):
    templ = cv2.imread(tmpName)
    #print('tmpName', tmpName)
    template = cv2.cvtColor(templ, cv2.COLOR_BGR2RGB)
    h, w = template.shape[:2]
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = confidence
    loc = np.where(res >= threshold)
    foundList = []
    mask = np.zeros(img.shape[:2], np.uint8)
    for pt in zip(*loc[::-1]):
        if mask[pt[1] + int(round(h / 2)), pt[0] + int(round(w / 2))] != 255:
            mask[pt[1]:pt[1] + h, pt[0]:pt[0] + w] = 255
            foundList.append([pt[0],pt[1],w,h])
    return foundList

def moveMouse(x,y):
    windll.user32.SetCursorPos(x, y)
    curx, cury = getCursorPos()
    if(curx != x or cury != y):
        moveMouse(x,y)

def captureMss(m):
    with mss() as sct:
        sct_img = sct.grab(m)
        return cv2.cvtColor(np.asarray(sct_img), cv2.COLOR_BGR2RGB)

def numberOcr(img, folder, thresh=0.85):
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    listOfFounds=[]
    for number in numbers:
        positions = locateAll("captcha/%s/%s.png" % (folder, number), img, confidence=thresh)
        for pos in positions:
            if (pos):
                item = {}
                item['left'] = pos[0]
                item['number'] = int(number)
                listOfFounds.append(item)
    sorted_list = sorted(listOfFounds, key=lambda d: int(d['left']))
    numberString = ''.join(str(e['number']) for e in sorted_list)
    return numberString

#Main function, m should be the game window
def sweepScreen(m):
    im = captureMss(m)
    res = locate("captcha/Recognition/robot.png", im, confidence=0.8)
    img_bwo = None
    goAhead = False
    if (res != None):
        #this is the area cropped for the inside of the captcha area
        area = (res[0] - 110, res[1] + 140, res[0] + 350, res[1] + 345)
        #I found 29 pixels to be a good range for the final image quality
        direction = True
        for x in range(area[0],area[2], 33):
            direction = not direction
            yRange = range(area[1], area[3], 29) if direction else range(area[3], area[1], -29)
            for y in yRange:
                xRange = random.uniform(x-16,x+16)
                moveMouse(int(m["left"]) + int(xRange), int(m["top"]) + int(y))
                img = captureMss(m)[area[1]:area[3],area[0]:area[2]]
                if (not goAhead):
                    img_bwo = img
                    goAhead = True
                else:
                    img_bwo = cv2.bitwise_or(img_bwo, img) #Every image is "added" to another using bitwise OR
                time.sleep(0.015)
        #the final image is transformed into a HSV representation image
        hsv = cv2.cvtColor(img_bwo, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([120, 255, 255])
        #than its filtered for masking it transparent with the highest contrast
        mask = cv2.inRange(hsv, lower_red, upper_red)
        #at final, the noise is removed using mathematical morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 8))
        morph_img = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return [cv2.cvtColor(morph_img, cv2.COLOR_BGR2RGB), True]
    else:
        return [False, False]

def slideAndDrop(m,number):
    im = captureMss(m)
    captchaPos = locate("captcha/Recognition/captchaBar.png", im, confidence=0.7)
    #print('captchaPos', captchaPos)
    if (captchaPos != None):
        robotPos = locate("captcha/Recognition/robot.png", im, confidence=0.8)
        newArea = {
            'left': m["left"]+robotPos[0]+30,
            'top': m["top"]+robotPos[1]+75,
            'width': 190,
            'height': 75
        }
        if(robotPos != None):
            captchaX = int(m["left"])+int(captchaPos[0]+int(captchaPos[2]/2))
            captchaY = int(m["top"])+int(captchaPos[1]+int(captchaPos[3]/2))
            robotX = int(m["left"]) + int(robotPos[0]+340)
            robotT = date.a(m["left"], m["top"])
            moveMouse(captchaX, captchaY)
            mouse.press(Button.left)
            moveMouse(captchaX+10, captchaY)
            time.sleep(0.2)
            for x in range(captchaX, robotX, 7):
                xRange = int(random.uniform(x - 3, x + 3))
                yRange = int(random.uniform(captchaY - 15, captchaY + 20))
                moveMouse(xRange, yRange)
                im = captureMss(newArea)
                currentNumber = numberOcr(im, "ocr")
                if(currentNumber == number):
                    print("Found")
                    break
                time.sleep(0.03)
            mouse.release(Button.left)

def solveCaptcha():
    time.sleep(10)
    gameList = getWindowsWithTitle('Bombcrypto')
    if (len(gameList) > 0):
        index = gameList.index(gameList[0])
        m = getDimensions(gameList[0])
        img = sweepScreen(m)
        if img[1] == False:
            return False
        else:
            number = numberOcr(img[0], "hsvOcr")
            print("Number to find: %s"%number)
            slideAndDrop(m,number)
        return True