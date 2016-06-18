# -*- coding: utf-8 -*-

'''
Created on 14.6.2016

@author: Kalmis
'''

from dateutil.parser import *
from dateutil.relativedelta import *


class JSONParser(object):
    '''
    Class for Parsing JSON. Methods of this class can be used to
    obtain e.g. Amica's menus
    '''

    def getAmicaDays(self, json):
        MenusForDays = json['MenusForDays']
        dates = []
        for day in MenusForDays:
            dates.append(parse(day['Date']))
        return dates

    def getAmicaMenuForDay(self, json, date):
        for day in json['MenusForDays']:
            MenuDate = parse(day['Date'])
            if date.date() == MenuDate.date():
                return day
        return 0

    def getAmicaMenuNamesForDate(self, json, date):
        names = []
        MenuForDay = self.getAmicaMenuForDay(json, date)
        for SetMenu in MenuForDay['SetMenus']:
            names.append(SetMenu['Name'])
        return names

    def getAmicaSetMenu(self, MenuForDay, menuName):
        for SetMenu in MenuForDay['SetMenus']:
            if SetMenu['Name'].lower() == menuName.lower():
                return SetMenu
        return 0

    def getAmicaSetMenuForDate(self, json, date, SetMenuName):

        MenuForDay = self.getAmicaMenuForDay(json, date)
        SetMenu = self.getAmicaSetMenu(MenuForDay, SetMenuName)
        setMenuString = ""
        for food in SetMenu['Components']:
            setMenuString += food + '\n'
        return setMenuString

    def getAmicaFullMenuForDate(self, json, date):
        setMenuNames = self.getAmicaMenuNamesForDate(json, date)
        returnText = ""
        for name in setMenuNames:
            returnText += name + '\n' + self.getAmicaSetMenu(json, date, name)
        return returnText
