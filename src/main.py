'''
Created on 17.5.2016

@author: Kalmis
'''

conf = 'bot.conf'

import telepot
import requests
import json
import configparser
import time
from bot import YourBot

class Main(object):
    '''
    Main program that uses the Bot class
    '''
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(conf)
        self.TOKEN = self.config['DEFAULTS']['Token']
        print("Config read")
        self.bot = YourBot(self.TOKEN)
        self.bot.downloadMenus(self.config)
        self.bot.message_loop()
        print('Started')

        while 1:
            time.sleep(10)


if __name__ == '__main__':
    Main()
