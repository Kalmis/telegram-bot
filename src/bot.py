'''
Created on 14.6.2016

@author: Kalmis
'''


import telepot
import requests
import json
import configparser


class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def downloadMenus(self,config):
        self.menus = {}
        for option in config.options('RESTAURANTS'):
            r = requests.get(config.get('RESTAURANTS',option))
            if r.status_code == 200:
                self.menus[option] = r.json()


    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('Chat:', content_type, chat_type, chat_id)

        if content_type != 'text':
            return

        command = msg['text'][1:].lower()
        msg_id = msg['message_id']

        if command in self.menus:
            self.sendMessage(chat_id, 'Tästä se alkaa', reply_to_message_id=msg_id)
