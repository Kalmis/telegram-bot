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
from pokemons import pokemon
import configparser
#import pprint
import feedparser
import geopy
import pytz
import json


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

    def initGeopyGoogle(self, TOKEN):
        self.GOOGLETOKEN = TOKEN
        self.geopyGoogle = geopy.geocoders.GoogleV3(self.GOOGLETOKEN, "maps.google.fi")

    def readSubwayMenu(self):
        categoryName = "SUBWAY"
        self.subwayMenu = {}
        for option in self.config.options(categoryName):
            fileName = self.config.get(categoryName, option)
            try:
                data_file = open(fileName)
                self.subwayMenu[option] = json.load(data_file)
            except Exception as e:
                print("Reading subway file was not succesfull.")
                print(e)

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

    def downloadHYYMenus(self):
        '''Downloads HYY menus that are set in config under [HYY], decodes RSS to
        dict and stores dicts in dict where option's name is the key'''
        categoryName = "HYY"
        self.HYYMenus = {}
        for option in self.config.options(categoryName):
            r = feedparser.parse(self.config.get(categoryName, option))
            if not r.bozo:
                self.HYYMenus[option] = r

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

    def getLocalTimeForLocationName(self, locationName):
        if locationName in self.config['LOCATIONNAMES']:
            locationName = self.config['LOCATIONNAMES'][locationName]

        returnText = ""
        location = self.geopyGoogle.geocode(locationName)
        if location is None:
            return None
        returnText += "{!s}\n".format(location.address)
        timeZoneId = self.getTimezoneIdForLocation(location)
        if timeZoneId is None:
            return None
        localTime = datetime.datetime.now(pytz.timezone(timeZoneId))
        returnText += localTime.strftime("%H:%M %z %Z %d.%m.%Y ")
        return returnText

    def getTimezoneIdForLocation(self, location):
        url = "https://maps.googleapis.com/maps/api/timezone/json?location="
        url += "{!s}".format(location.latitude)
        url += ","
        url += "{!s}".format(location.longitude)
        url += "&timestamp="
        url += "{!s}".format(int(datetime.datetime.now().timestamp()))
        url += "&key="
        url += "{!s}".format(self.GOOGLETOKEN)

        r = requests.get(url)
        if r.status_code == 200:
            return r.json()['timeZoneId']

    def on_message(self, msg):
        '''On every message this method is called. All command's logic are here'''
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            return

        query = msg['text'].split()
        # Commands may be in form /rafla or /rafla@botname
        command = query[0].split('@')[0][1:].lower()

        msg_id = msg['message_id']
        print('Chat:', content_type, chat_type, chat_id, msg['text'])

        if command == 'help':
            reply = ""
            reply += "/pokemon Päivän pokemon!\n"
            reply += "/time Local time of given location (address, city etc.)\n"
            reply += "Menu of restaurant:\n"
            restaurants = list(self.amicaMenus) + list(self.sodexoMenus) + \
                list(self.taffaMenu) + list(self.HYYMenus) + list(self.subwayMenu)
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

        elif command in self.HYYMenus:
            today = datetime.datetime.now()
            fullMenu = menuParser.getHYYFullMenuForDate(self.HYYMenus[command], today)
            if len(fullMenu) > 0:
                reply = "{!s}\n".format(today.strftime("%A %d.%m.%Y"))
                reply += fullMenu
            else:
                reply = "Ei listaa tälle päivälle"
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)

        elif command in self.subwayMenu:
            today = datetime.datetime.now()
            fullMenu = menuParser.getSubwaySubOfTheDay(self.subwayMenu[command], today)
            reply = "{!s}\n {!s}".format(today.strftime("%A"), fullMenu)
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)


        elif command == 'time':
            if len(query) < 2:
                reply = "Anna sijainti"
            else:
                reply = self.getLocalTimeForLocationName(' '.join(query[1:]))
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)

        elif command == 'pokemon':
            reply = pokemon.getTodaysPokemon()
            self.sendMessage(chat_id, reply, reply_to_message_id=msg_id)
