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
from bs4 import BeautifulSoup
from dateutil.parser import parse
import pprint


class YourBot(telepot.Bot):

    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def readConfigs(self, config):
        self.config = configparser.ConfigParser()
        self.config.read(config)
        print("Config read")

    def downloadAmicaMenus(self):
        categoryName = "AMICA"
        self.amicaMenus = {}
        for option in self.config.options(categoryName):
            r = requests.get(self.config.get(categoryName, option))
            if r.status_code == 200:
                self.amicaMenus[option] = r.json()

    def downloadSodexoMenus(self):
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

    def downloadTaffaMenus(self):
        categoryName = "TAFFA"
        self.taffaMenu = {}
        for option in self.config.options(categoryName):
            r = requests.get(self.config.get(categoryName, option))
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                temp = {"class": "todays-menu"}
                todays_menu = soup.find(attrs=temp)
                courses = []
                for li in todays_menu.ul.children:
                    if li.name == "li":
                        temp = {"title_fi": li.contents[0]}
                        courses.append(temp)
                self.taffaMenu['courses'] = courses

    def on_message(self, msg):
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
            restaurants = list(self.amicaMenus) + list(self.sodexoMenus)
            restaurants.sort()
            for restaurant in restaurants:
                reply += "/{!s}\n".format(restaurant)
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)

        elif command in self.amicaMenus:
            today = datetime.datetime.now()
            fullMenu = menuParser.getAmicaFullMenuForDate(self.amicaMenus[command], today)
            if len(fullMenu) > 0:
                reply = fullMenu
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
