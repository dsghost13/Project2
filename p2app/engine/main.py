# p2app/engine/main.py
#
# ICS 33 Fall 2024
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.

import os
import sqlite3
from webbrowser import Error

from p2app.events import *

class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self.connection = None


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        #----------#
        # Database #
        #----------#

        if isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()

        elif isinstance(event, OpenDatabaseEvent):
            try:
                file_extension = os.path.splitext(event.path())[-1]
                if file_extension == '.db':
                    self.connection = sqlite3.connect(event.path())
                    yield DatabaseOpenedEvent(event.path())
                else:
                    raise sqlite3.Error
            except sqlite3.Error:
                yield DatabaseOpenFailedEvent('Database Open Failed')

        #-------------#
        # Application #
        #-------------#

        elif isinstance(event, CloseDatabaseEvent):
            yield DatabaseClosedEvent()

        #-----------#
        # Continent #
        #-----------#

        elif isinstance(event, StartContinentSearchEvent):
            # gets entered parameters
            continent_code = event.continent_code()
            name = event.name()

            # generates WHERE statement
            where_statement = f'WHERE continent_code = \'{continent_code}\' AND name = \'{name}\''
            if not continent_code:
                where_statement = f'WHERE name = \'{name}\''
            elif not name:
                where_statement = f'WHERE continent_code = \'{continent_code}\''

            # retrieves matching continents
            cursor = self.connection.execute(f'''SELECT * FROM continent {where_statement};''')
            for continent in cursor:
                yield ContinentSearchResultEvent(Continent(*continent))

        #---------#
        # Country #
        #---------#

        elif isinstance(event, StartCountrySearchEvent):
            # gets entered parameters
            country_code = event.country_code()
            name = event.name()

            # generates WHERE statement
            where_statement = f'WHERE country_code = \'{country_code}\' AND name = \'{name}\''
            if not country_code:
                where_statement = f'WHERE name = \'{name}\''
            elif not name:
                where_statement = f'WHERE country_code = \'{country_code}\''

            # retrieves matching countries
            cursor = self.connection.execute(f'''SELECT * FROM country {where_statement};''')
            for country in cursor:
                yield CountrySearchResultEvent(Country(*country))

        #--------#
        # Region #
        #--------#

        elif isinstance(event, StartRegionSearchEvent):
            # gets entered parameters
            region_code = event.region_code()
            local_code = event.local_code()
            name = event.name()

            # scenario with all parameters entered
            columns = [region_code, local_code, name]
            params = [f'region_code = \'{region_code}\'',
                      f'local_code = \'{local_code}\'',
                      f'name =\'{name}\'']

            # removes unentered parameters
            for i in range(2, -1, -1):
                if not columns[i]:
                    del params[i]

            # generates WHERE statement
            where_statement = ''
            for param in params:
                if not where_statement:
                    where_statement += 'WHERE ' + param
                else:
                    where_statement += 'AND ' + param

            # retrieves matching regions
            cursor = self.connection.execute(f'''SELECT * FROM region {where_statement};''')
            for region in cursor:
                yield RegionSearchResultEvent(Region(*region))