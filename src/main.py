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
        config = configparser.ConfigParser()
        config.read(conf)
        TOKEN = config['DEFAULTS']['Token']

        # Create bot object, download menus set in config and start loop
        self.bot = YourBot(TOKEN)
        self.bot.readConfigs(conf)
        self.downloadMenus()
        self.bot.message_loop(self.bot.on_message)

        # Download menus every 6 hours to keep them up to date
        schedule.every(6).hours.do(self.downloadMenus)
        print('Started')

        while 1:
            schedule.run_pending()
            time.sleep(10)

    def downloadMenus(self):
        self.bot.downloadSodexoMenus()
        self.bot.downloadAmicaMenus()

if __name__ == '__main__':
    Main()
