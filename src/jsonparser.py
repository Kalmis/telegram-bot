# -*- coding: utf-8 -*-

'''
Created on 14.6.2016

@author: Kalmis
'''

from dateutil.parser import *
from dateutil.relativedelta import *
import datetime


class JSONParser(object):
    '''
    Class for Parsing JSON. Methods of this class can be used to obtain e.g. Amica's menus
    '''

    def getAmicaDays(self,json):
        MenusForDays = json['MenusForDays']
        dates = []
        for day in MenusForDays:
            dates.append(parse(day['Date']))
        return dates


    def getAmicaMenuForDay(self,json,date):
        for day in json['MenusForDays']:
            MenuDate = parse(day['Date'])
            if date.date() == MenuDate.date():
                return day
        return 0

    def getAmicaSetMenu(self,MenuForDay,menuName):
        for SetMenu in MenuForDay['SetMenus']:
            if SetMenu['Name'].lower() == menuName.lower():
                return SetMenu
        return 0


    def getAmicaSetMenuForDate(self,json,date,SetMenuName):

        MenuForDay=self.getAmicaMenuForDay(json,date)
        SetMenu = self.getAmicaSetMenu(MenuForDay,SetMenuName)
        setMenuString = ""
        for food in SetMenu['Components']:
            setMenuString+=food+'\n'
        return setMenuString
