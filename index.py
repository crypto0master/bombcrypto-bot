# -*- coding: utf-8 -*-   
from PIL import Image 
from cv2 import cv2

from captcha.solveCaptcha import solveCaptcha


from os import listdir
from src.logger import logger, loggerMapClicked
from random import randint
from random import random


import numpy as np
import mss
import pyautogui
import time
import sys

import yaml
import telebot



if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    c = yaml.safe_load(stream)

ct = c['threshold']
ch = c['home']

if not ch['enable']:
    print('>>---> Home feature not enabled')
print('\n')

pyautogui.PAUSE = c['time_intervals']['interval_between_moviments']

pyautogui.FAILSAFE = False
hero_clicks = 0
login_attempts = 0
last_log_is_progress = False
logo_found = 0

bot = telebot.TeleBot(c["telegram_token"])
account_id = '#' + str(c['accountid'])

def addRandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images():
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

images = load_images()

def loadHeroesToSendHome():
    file_names = listdir('./targets/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d heroes that should be sent home loaded' % len(heroes))
    return heroes

if ch['enable']:
    home_heroes = loadHeroesToSendHome()

# go_work_img = cv2.imread('targets/go-work.png')
# commom_img = cv2.imread('targets/commom-text.png')
# arrow_img = cv2.imread('targets/go-back-arrow.png')
# hero_img = cv2.imread('targets/hero-icon.png')
# x_button_img = cv2.imread('targets/x.png')
# teasureHunt_icon_img = cv2.imread('targets/treasure-hunt-icon.png')
# ok_btn_img = cv2.imread('targets/ok.png')
# connect_wallet_btn_img = cv2.imread('targets/connect-wallet.png')
# select_wallet_hover_img = cv2.imread('targets/select-wallet-1-hover.png')
# select_metamask_no_hover_img = cv2.imread('targets/select-wallet-1-no-hover.png')
# sign_btn_img = cv2.imread('targets/select-wallet-2.png')
# new_map_btn_img = cv2.imread('targets/new-map.png')
# green_bar = cv2.imread('targets/green-bar.png')
full_stamina = cv2.imread('targets/full-stamina.png')

robot = cv2.imread('targets/robot.png')
# puzzle_img = cv2.imread('targets/puzzle.png')
# piece = cv2.imread('targets/piece.png')
slider = cv2.imread('targets/slider.png')



def show(rectangles, img = None):

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)





def clickBtn(img,name=None, timeout=3, threshold = ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
        # print('waiting for "{}" button, timeout of {}s'.format(name, timeout))
    start = time.time()
    clicked = False
    while(not clicked):
        matches = positions(img, threshold=threshold)
        if(len(matches)==0):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        # mudar moveto pra w randomness
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True

def clickBtnRight(img,name=None, timeout=3, threshold = ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
        # print('waiting for "{}" button, timeout of {}s'.format(name, timeout))
    start = time.time()
    clicked = False
    while(not clicked):
        matches = positions(img, threshold=threshold)
        if(len(matches)==0):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        # mudar moveto pra w randomness
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click(button='right')
        return True

def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:,:,:3]




def positions(target, threshold=ct['default'], scr='false'):
    now = time.time()
    img = printSreen()
    image = printSreen()
    if(scr=='tr'):
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'screen{}.png'.format(now))
        image = cv2.imread('screen{}.png'.format(now))    
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])


    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def scroll():

    commoms = positions(images['commom-text'], threshold = ct['commom'])
    if (len(commoms) == 0):
        return
    x,y,w,h = commoms[len(commoms)-1]
#
    moveToWithRandomness(x,y,1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')


def clickButtons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    for (x, y, w, h) in buttons:
        moveToWithRandomness(x+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(buttons)

def isHome(hero, buttons):
    y = hero[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            # if send-home button exists, the hero is not home
            return False
    return True

def isWorking(bar, buttons):
    y = bar[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def randomMove():
    arrow_pos = positions(images['go-back-arrow'], threshold=0.75, scr="false")
    if(len(arrow_pos)==0):
        print("arrow not found")
        return

    x,y,w,h = arrow_pos[len(arrow_pos)-1]
    #x = x - 1;
    arrow_pos = {
        "x": x,
        "y": y,
        "w": w,
        "h": h
    }

    pyautogui.moveTo(arrow_pos["x"] + randint(100, 400), arrow_pos["y"] + randint(50, 250), 1);
    pyautogui.moveTo(arrow_pos["x"] + randint(100, 400), arrow_pos["y"] + randint(50, 250), 1);



def clickGreenBarButtons():
    # ele clicka nos q tao trabaiano mas axo q n importa
    offset = 130

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d buttons detected' % len(buttons))


    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d buttons with green bar detected' % len(not_working_green_bars))
        logger('👆 Clicking in %d heroes' % len(not_working_green_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        if hero_clicks > 20:
            logger('⚠️ Too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_working_green_bars)

def clickFullBarButtons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicking in %d heroes' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)

def goToHeroes():
    if clickBtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    solveCaptcha()
    #TODO tirar o sleep quando colocar o pulling
    time.sleep(1)
    clickBtn(images['hero-icon'])
    time.sleep(1)
    solveCaptcha()

def goToGame():
    # in case of server overload popup
    clickBtn(images['x'])
    # time.sleep(3)
    clickBtn(images['x'])

    clickBtn(images['treasure-hunt-icon'])
    clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout = 10)

def refreshHeroesPositions():

    logger('🔃 Refreshing Heroes Positions')
    clickBtn(images['go-back-arrow'])
    clickBtn(images['treasure-hunt-icon'])

    # time.sleep(3)
    clickBtn(images['treasure-hunt-icon'])

def login():
    global login_attempts
    logger('😿 Checking if game has disconnected')

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

   #positions(images['connect-wallet'], threshold=ct['default'], scr='tr')
    if clickBtn(images['connect-wallet'], name='connectWalletBtn', timeout = 10):
        solveCaptcha()
        login_attempts = login_attempts + 1
        logger('🎉 Connect wallet button detected, logging in!')
        #TODO mto ele da erro e poco o botao n abre
        time.sleep(10)

    if clickBtn(images['select-wallet-2'], name='sign button', timeout=8):
        # sometimes the sign popup appears imediately
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        if clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout = 15):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        return
        # click ok button


    if clickBtn(images['select-wallet-2'], name='signBtn', timeout = 20):
        login_attempts = login_attempts + 1
        print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        time.sleep(25)
        if clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout=30):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        # time.sleep(15)

    if clickBtn(images['ok'], name='okBtn', timeout=5):
        pass
        # time.sleep(15)
        # print('ok button clicked')
    if clickBtn(images['treasure-hunt-icon'], name='treasure', timeout=5):
        pass

    if clickBtn(images['x'], name='okBtn', timeout=5):
        pass



def sendHeroesHome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len (hero_positions) == 0:
            #TODO maybe pick up match with most wheight instead of first
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('No heroes that should be sent home found.')
        return
    print(' %d heroes that should be sent home found' % n)
    # if send-home button exists, the hero is not home
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])
    # TODO pass it as an argument for both this and the other function that uses it
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not isHome(position,go_home_buttons):
            print(isWorking(position, go_work_buttons))
            if(not isWorking(position, go_work_buttons)):
                print ('hero not working, sending him home')
                moveToWithRandomness(go_home_buttons[0][0]+go_home_buttons[0][2]/2,position[1]+position[3]/2,1)
                pyautogui.click()
            else:
                print ('hero working, not sending him home(no dark work button)')
        else:
            print('hero already home, or home full(no dark home button)')





def refreshHeroes():

    global hero_clicks

    logger('🏢 Search for heroes to work')

    goToHeroes()

    if c['select_heroes_mode'] == "full":
        logger('⚒️ Sending heroes with full stamina bar to work', 'green')
    elif c['select_heroes_mode'] == "green":
        logger('⚒️ Sending heroes with green stamina bar to work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']

    while(empty_scrolls_attempts >0):
        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
        elif c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons()
        else:
            buttonsClicked = clickButtons()

        sendHeroesHome()

        if buttonsClicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
        scroll()
        time.sleep(2)
    logger('💪 {} heroes sent to work'.format(hero_clicks))
    if(c["log_telegram"] == True):
        bot.send_message(c["telegram_chat_id"], "BOMBCRYPTO " + account_id + " HERO CLICKS {} ".format(hero_clicks))
    hero_clicks = 0
    goToGame()


last = {
"login" : 0,
"heroes" : 0,
"new_map" : 0,
"check_for_captcha" : 0,
"refresh_heroes" : 0,
"check_logo": 0,
"check_for_error": 0,
"screen": 0,
"balance": 0,
"check_logo": 0,
"check_chrome_alert": 0,
"backg": 0,
"mmopen": 0,
"error": 0,
"randmove": 0
}

def check_logo():
    now = time.time()
    global last, logo_found
    sys.stdout.write("\nChecking logo.")
    sys.stdout.flush()
    last["check_logo"] = now
    if clickBtn(images['logo'], name='logo', timeout = 3, threshold=0.8):  
        sys.stdout.write('\nLogo found, refreshing\n')
        last["heroes"] = 0
        last["login"] = 0
        logo_found = 1
        pyautogui.hotkey('ctrl','f5')
        time.sleep(10)

def takeScreenshot():
    sys.stdout.write('\n Taking screenshot')
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(r'screen.png')
    photo = open('screen.png', 'rb')
    if(c["log_telegram"] == True):
        bot.send_message(c["telegram_chat_id"], "BOMBCRYPTO " + account_id + " screenshot")
        bot.send_photo(c["telegram_chat_id"], photo)

def sendBalance():
    sys.stdout.write('\n Taking screenshot balance')
    if clickBtn(images['balance'], name='balance', timeout = 10, threshold=0.6):  
        time.sleep(3)  
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'screen.png')
        photo = open('screen.png', 'rb')
        if(c["log_telegram"] == True):
            bot.send_message(c["telegram_chat_id"], "BOMBCRYPTO " + account_id + " BALANCE")
            bot.send_photo(c["telegram_chat_id"], photo)
        clickBtn(images['x'])
        clickBtn(images['x'])

def main():

    global last, logo_found

    if(c["log_telegram"] == True):
        bot.send_message(c["telegram_chat_id"], "BOMBCRYPTO " + account_id + " started")
    time.sleep(5)
    t = c['time_intervals']



    while True:
        now = time.time()

        if now - last["mmopen"] > 1 * 60:
            sys.stdout.write("\nChecking mmopen.")
            last["mmopen"] = now
            if clickBtn(images['mmopen'], name='mmopen', timeout = 3, threshold=0.9):  
                if clickBtn(images['select-wallet-2'], name='sign button', timeout=8):  
                    sys.stdout.write('\nmm closed, refreshing\n')
                    last["heroes"] = 0
                    last["login"] = 0
                    clickBtn(images['reload'], name='reload', timeout=8)
                    pyautogui.hotkey('ctrl','f5')
                    time.sleep(10)
                    continue

        if now - last["error"] > 1 * 60:
            sys.stdout.write("\nChecking error.")
            last["error"] = now
            if clickBtn(images['error'], name='error', timeout = 3, threshold=0.7):  
                sys.stdout.write('\nerror found, refreshing\n')
                last["heroes"] = 0
                last["login"] = 0
                clickBtn(images['reload'], name='reload', timeout=8)
                pyautogui.hotkey('ctrl','f5')
                time.sleep(10)
                continue

        if now - last["login"] > addRandomness(t['check_for_login'] * 60):
            sys.stdout.flush()
            last["login"] = now
            login()

        if logo_found == 1:
            logo_found = 0
            continue

        if now - last["check_logo"] > 1 * 60 :
            check_logo()

        if logo_found == 1:
            logo_found = 0
            continue

        if now - last["backg"] > 1 * 60 :
            sys.stdout.write("\nChecking backg.")
            sys.stdout.flush()
            last["backg"] = now
            if clickBtn(images['backg'], name='backg', timeout = 3, threshold=0.6):  
                sys.stdout.write('\nbackg found, refreshing\n')
                last["heroes"] = 0
                pyautogui.hotkey('ctrl','f5')
                time.sleep(10)
                continue

        if now - last["check_for_captcha"] > addRandomness(t['check_for_captcha'] * 60):
            last["check_for_captcha"] = now
            solveCaptcha()

        if logo_found == 1:
            logo_found = 0
            continue

        if now - last["check_chrome_alert"] > 1 * 60 :
            sys.stdout.write("\nChecking chrome alert.")
            sys.stdout.flush()
            last["check_chrome_alert"] = now
            if clickBtn(images['ok_chrome'], name='ok_chrome', timeout = 3, threshold=0.7):  
                sys.stdout.write('\nok_chrome found, refreshing\n')
                pyautogui.hotkey('ctrl','f5')
                time.sleep(10)
                continue

        if logo_found == 1:
            logo_found = 0
            continue

        if now - last["screen"] > 7 * 60:
            last["screen"] = now
            takeScreenshot()
            sys.stdout.write("\n")

        if logo_found == 1:
            logo_found = 0
            continue

        if now - last["balance"] > 60 * 60:
            last["balance"] = now
            sendBalance()
            sys.stdout.write("\n")

        if logo_found == 1:
            logo_found = 0
            continue 

        if now - last["heroes"] > addRandomness(t['send_heroes_for_work'] * 60):
            last["heroes"] = now
            refreshHeroes()

        if logo_found == 1:
            logo_found = 0
            continue

        if now - last["new_map"] > t['check_for_new_map_button']:
            last["new_map"] = now

            if clickBtn(images['new-map']):
                logger('NEW MAP')
                if(c["log_telegram"] == True):
                    bot.send_message(c["telegram_chat_id"], "BOMBCRYPTO " + account_id + " NEW MAP")

        if logo_found == 1:
            logo_found = 0
            continue

        if now - last["refresh_heroes"] > addRandomness( t['refresh_heroes_positions'] * 60):
            solveCaptcha()
            last["refresh_heroes"] = now
            refreshHeroesPositions()

        if now - last["randmove"] > addRandomness( 1 * 60):
            randomMove()
            last["randmove"] = now

        #clickBtn(teasureHunt)
        logger(None, progress_indicator=True)

        sys.stdout.flush()

        time.sleep(1)

main()

