# -*- coding: utf-8 -*-

'''
Created on 14.6.2016

@author: Kalmis
'''

from dateutil.parser import parse
from bs4 import BeautifulSoup
from datetime import datetime


class menuParser(object):
    '''
    Class for Parsing dict. Methods of this class can be used to
    obtain e.g. Amica's menus
    '''
    @staticmethod
    def getAmicaDays(dict):
        ''' From given Amica menu dict, returns dates for given menus'''
        MenusForDays = dict['MenusForDays']
        dates = []
        for day in MenusForDays:
            dates.append(parse(day['Date']))
        return dates

    @staticmethod
    def getAmicaMenuForDay(dict, date):
        '''Returns menu dict for given day'''
        for day in dict['MenusForDays']:
            MenuDate = parse(day['Date'])
            if date.date() == MenuDate.date():
                return day
        return {'SetMenus': []}

    @staticmethod
    def getAmicaMenuNamesForDate(dict, date):
        ''' From given Amica menu dict, returns menu names for given day'''
        names = []
        MenuForDay = menuParser.getAmicaMenuForDay(dict, date)
        for SetMenu in MenuForDay['SetMenus']:
            names.append(SetMenu['Name'])
        return names

    @staticmethod
    def getAmicaSetMenu(MenuForDay, menuName):
        '''Get food of given menu'''
        for SetMenu in MenuForDay['SetMenus']:
            if SetMenu['Name'].lower() == menuName.lower():
                return SetMenu
        return {'Components': ""}

    @staticmethod
    def getAmicaSetMenuForDate(dict, date, SetMenuName):
        '''Get food for given day and menu name'''
        MenuForDay = menuParser.getAmicaMenuForDay(dict, date)
        SetMenu = menuParser.getAmicaSetMenu(MenuForDay, SetMenuName)
        setMenuString = ""
        for food in SetMenu['Components']:
            setMenuString += food + '\n'
        return setMenuString

    @staticmethod
    def getAmicaFullMenuForDate(dict, date):
        '''Get all foods of given day'''
        setMenuNames = menuParser.getAmicaMenuNamesForDate(dict, date)
        returnText = ""
        for name in setMenuNames:
            food = menuParser.getAmicaSetMenu(dict, date, name)
            returnText += "{!s}\n {!s}".format(name, food)
        return returnText

    @staticmethod
    def getSodexoFullMenu(dict):
        '''Get all foods of given dict'''
        returnText = ""
        date = datetime.fromtimestamp(float(dict['meta']['requested_timestamp']))
        returnText += "{!s}\n".format(date.strftime("%A %d.%m.%Y"))
        for course in dict['courses']:
            food = course['title_fi']
            try:
                allergens = course['properties']
            except KeyError:
                allergens = ""
            returnText += "{!s} ({!s})\n".format(food, allergens)
        return returnText

    @staticmethod
    def parseTaffaTodaysMenu(html):
        menu = {}

        soup = BeautifulSoup(html, 'html.parser')
        temp = {"class": "todays-menu"}
        todays_menu = soup.find(attrs=temp)

        date = parse(todays_menu.p.contents[0].split()[-1])
        meta = {"requested_timestamp": str(date.timestamp())}
        courses = []
        for li in todays_menu.ul.children:
            if li.name == "li":
                # The page's encoding isn't utf-8 after all...
                content = str(li.contents[0]).encode('latin-1').decode('utf-8')
                temp = {"title_fi": content}
                courses.append(temp)
        menu['courses'] = courses
        menu['meta'] = meta
        return menu
