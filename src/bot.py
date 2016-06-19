# -*- coding: utf-8 -*-

'''
Created on 14.6.2016

@author: Kalmis
'''


import telepot
import requests
import datetime
from furl import furl  # For manipulating sodexo urls
from menuparser import menuParser
import configparser
import pprint


class YourBot(telepot.Bot):

    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def readConfigs(self, config):
        '''Reads configs from given file to memory'''
        self.config = configparser.ConfigParser()
        self.config.read(config)
        print("Config read")

    def downloadAmicaMenus(self):
        '''Downloads amica menus that are set in config under [AMICA], decodes JSON to
        dict and stores dicts in dict where option's name is the key'''
        categoryName = "AMICA"
        self.amicaMenus = {}
        for option in self.config.options(categoryName):
            r = requests.get(self.config.get(categoryName, option))
            if r.status_code == 200:
                self.amicaMenus[option] = r.json()

    def downloadSodexoMenus(self):
        '''Downloads sodexo menus that are set in config under [AMICA], decodes json to
        dict and stores dicts in dict where option's name is the key'''
        categoryName = "SODEXO"
        self.sodexoMenus = {}
        today = datetime.datetime.now().date()
        for option in self.config.options(categoryName):
            url = furl(self.config.get(categoryName, option))
            url.path.segments[4] = str(today.year)
            url.path.segments[5] = str(today.month)
            url.path.segments[6] = str(today.day)
            r = requests.get(url.url)
            if r.status_code == 200:
                self.sodexoMenus[option] = r.json()

    def downloadTaffaMenu(self):
        '''Downloads Täffä's todays menu from their website and stores it in same
        dict structure as Sodexo menus'''
        categoryName = "TAFFA"
        self.taffaMenu = {}
        for option in self.config.options(categoryName):
            r = requests.get(self.config.get(categoryName, option))
            if r.status_code == 200:
                menu = menuParser.parseTaffaTodaysMenu(r.text)
                menu['meta']['ref_title'] = "Täffä"
                menu['meta']['ref_url'] = self.config.get(categoryName, option)
                self.taffaMenu[option] = menu

    def on_message(self, msg):
        '''On every message this method is called. All command's logic are here'''
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('Chat:', content_type, chat_type, chat_id)

        if content_type != 'text':
            return

        query = msg['text'].split()
        # Commands may be in form /rafla or /rafla@botname
        command = query[0].split('@')[0][1:].lower()

        msg_id = msg['message_id']

        if command == 'help':
            reply = ""
            reply += "Menu of restaurant:\n"
            restaurants = list(self.amicaMenus) + list(self.sodexoMenus) + \
                list(self.taffaMenu)
            restaurants.sort()
            for restaurant in restaurants:
                reply += "/{!s}\n".format(restaurant)
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)

        elif command in self.amicaMenus:
            today = datetime.datetime.now()
            fullMenu = menuParser.getAmicaFullMenuForDate(self.amicaMenus[command], today)
            if len(fullMenu) > 0:
                reply = "{!s}\n".format(today.strftime("%A %d.%m.%Y"))
                reply += fullMenu
            else:
                reply = "Ei listaa tälle päivälle"
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)

        elif command in self.sodexoMenus:
            fullMenu = menuParser.getSodexoFullMenu(self.sodexoMenus[command])
            if len(fullMenu) > 0:
                reply = fullMenu
            else:
                reply = "Ei listaa tälle päivälle"
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)

        elif command in self.taffaMenu:
            fullMenu = menuParser.getSodexoFullMenu(self.taffaMenu[command])
            if len(fullMenu) > 0:
                reply = fullMenu
            else:
                reply = "Ei listaa tälle päivälle"
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)
