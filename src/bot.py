# -*- coding: utf-8 -*-

'''
Created on 14.6.2016

@author: Kalmis
'''


import telepot
import requests
import datetime
import pprint
from furl import furl  # For manipulating sodexo urls
from menuparser import menuParser


class YourBot(telepot.Bot):

    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def downloadAmicaMenus(self, config):
        self.amicaMenus = {}
        for option in config.options('AMICA'):
            r = requests.get(config.get('AMICA', option))
            if r.status_code == 200:
                self.amicaMenus[option] = r.json()

    def downloadSodexoMenus(self, config):
        self.sodexoMenus = {}
        #today = datetime.datetime.now().date()
        today = datetime.date(2016,6,17)
        for option in config.options('SODEXO'):
            url = furl(config.get('SODEXO', option))
            url.path.segments[4] = str(today.year)
            url.path.segments[5] = str(today.month)
            url.path.segments[6] = str(today.day)
            r = requests.get(url.url)
            if r.status_code == 200:
                self.sodexoMenus[option] = r.json()

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('Chat:', content_type, chat_type, chat_id)

        if content_type != 'text':
            return

        query = msg['text'].split()
        # Commands may be in form /rafla or /rafla@botname
        command=query[0].split('@')[0][1:].lower()

        msg_id = msg['message_id']

        if command in self.amicaMenus:
            today = datetime.datetime.now()
            fullMenu = menuParser.getAmicaFullMenuForDate(self.amicaMenus[command], today)
            if len(fullMenu) > 0:
                reply = fullMenu
            else:
                reply = "Ei listaa tälle päivälle"
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)
