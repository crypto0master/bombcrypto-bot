# bombcrypto-bot
Full autoplay bot for bombcrypto game with captcha solver and telegram logs


![Captcha](https://github.com/crypto0master/bombcrypto-bot/blob/main/readme-images/captcha.gif)


To use:
  
  `pip install -r requirements.txt`
  
  `python index.py`

Requirements:
Python version 3.8 for some libs

# HOT TO USE

Install [python 3.8](https://www.python.org/downloads/release/python-380/).

Before install make sure that checkbox "Add Python to PATH" is checked 
![Check Add python to PATH](https://github.com/crypto0master/bombcrypto-bot/blob/main/readme-images/pythontopath.png)


Unzip the bot folder and copy the path

![Copy PATH](https://github.com/crypto0master/bombcrypto-bot/blob/main/readme-images/address.png)

Press win+R put "cmd" and open command line 

![CMD](https://github.com/crypto0master/bombcrypto-bot/blob/main/readme-images/cmd.png)

write "cd" + path to bot 
![CD](https://github.com/crypto0master/bombcrypto-bot/blob/main/readme-images/cd.png)

### install requirements
write to cmd 
```
pip3 install -r requirements.txt
```
![PIP](https://github.com/crypto0master/bombcrypto-bot/blob/main/readme-images/pip.png)

### Start bot
```
python index.py
```
![RUN](https://github.com/crypto0master/bombcrypto-bot/blob/main/readme-images/run.png)


# HOT TO SEND SCREENSHOTS TO TELEGRAM
![RUN](https://github.com/crypto0master/bombcrypto-bot/blob/main/readme-images/telegram.png)

1. Go to official telegram [BotFather](https://t.me/BotFather/).
2. Create your bot and copy bot-token (eg. 5021546203:AAHeK199jW25dfvslkOhMzAumzVecSxvVZw )
4. Open config.yaml in your bot folder and paste bot-token to "telegram_token" 
5. In config.yaml set "log_telegram" to "True"
6. Go to [userinfobot](https://t.me/userinfobot) , send "/start" and copy your telegram id
7. In config.yaml set "telegram_chat_id" to your telegram_id
8. Go to your telegram bot and send "/start"
9. Start bot
