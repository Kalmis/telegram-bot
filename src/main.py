# -*- coding: utf-8 -*-

'''
Created on 17.5.2016

@author: Kalmis
'''

import configparser
import time
from bot import YourBot
import schedule
conf = 'bot.conf'


class Main(object):
    '''
    Main program that uses the Bot class
    '''
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(conf)
        self.TOKEN = self.config['DEFAULTS']['Token']
        print("Config read")

        # Create bot object, download menus set in config and start loop
        self.bot = YourBot(self.TOKEN)
        self.downloadMenus()
        self.bot.message_loop()

        # Download menus every 6 hours to keep them up to date
        schedule.every(6).hour.do(self.downloadMenus)
        print('Started')

        while 1:
            schedule.run_pending()
            time.sleep(10)

    def downloadMenus(self):
        self.bot.downloadMenus(self.config)

if __name__ == '__main__':
    Main()
