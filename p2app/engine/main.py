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
                # opens file if it's a database
                file_extension = os.path.splitext(event.path())[-1]
                if file_extension == '.db':
                    self.connection = sqlite3.connect(event.path())
                    yield DatabaseOpenedEvent(event.path())
                else:
                    yield DatabaseOpenFailedEvent('Not a Database File')
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
            where_statement = f'continent_code = \'{continent_code}\' AND name = \'{name}\''
            if not continent_code:
                where_statement = f'name = \'{name}\''
            elif not name:
                where_statement = f'continent_code = \'{continent_code}\''

            # retrieves matching continents
            cursor = self.connection.execute(f'''SELECT * 
                                                 FROM continent 
                                                 WHERE {where_statement};''')
            for continent in cursor:
                yield ContinentSearchResultEvent(Continent(*continent))

        elif isinstance(event, LoadContinentEvent):
            # displays data of chosen continent
            continent_id = event.continent_id()
            cursor = self.connection.execute(f'''SELECT * 
                                                 FROM continent 
                                                 WHERE continent_id = {continent_id};''')
            yield ContinentLoadedEvent(Continent(*cursor.fetchone()))

        elif isinstance(event, SaveNewContinentEvent):
            try:
                continent = list(event.continent())

                # generates new continent_id
                cursor = self.connection.execute(f'''SELECT continent_id
                                                     FROM continent ORDER BY continent_id DESC;''')
                continent[0] = cursor.fetchone()[0] + 1

                # inserts new continent
                continent = tuple(continent)
                self.connection.execute(f'''INSERT INTO continent (continent_id, continent_code, name) 
                                            VALUES {continent};''')
                yield ContinentSavedEvent(Continent(*continent))

            except sqlite3.Error:
                yield SaveContinentFailedEvent('Save Continent Failed')

        elif isinstance(event, SaveContinentEvent):
            try:
                continent = event.continent()

                # updates continent
                self.connection.execute(f'''UPDATE continent
                                            SET continent_code = \'{continent[1]}\',
                                                name = \'{continent[2]}\'
                                            WHERE continent_id = {continent[0]};''')
                yield ContinentSavedEvent(continent)
            except sqlite3.Error:
                yield SaveContinentFailedEvent('Save Continent Failed')

        #---------#
        # Country #
        #---------#

        elif isinstance(event, StartCountrySearchEvent):
            # gets entered parameters
            country_code = event.country_code()
            name = event.name()

            # generates WHERE statement
            where_statement = f'country_code = \'{country_code}\' AND name = \'{name}\''
            if not country_code:
                where_statement = f'name = \'{name}\''
            elif not name:
                where_statement = f'country_code = \'{country_code}\''

            # retrieves matching countries
            cursor = self.connection.execute(f'''SELECT * 
                                                 FROM country 
                                                 WHERE {where_statement};''')
            for country in cursor:
                yield CountrySearchResultEvent(Country(*country))

        elif isinstance(event, LoadCountryEvent):
            # displays data of chosen country
            country_id = event.country_id()
            cursor = self.connection.execute(f'''SELECT * 
                                                 FROM country 
                                                 WHERE country_id = {country_id};''')
            yield CountryLoadedEvent(Country(*cursor.fetchone()))

        elif isinstance(event, SaveNewCountryEvent):
            try:
                country = list(event.country())

                # checks for valid continent_id
                cursor = self.connection.execute(f'''SELECT continent_id 
                                                     FROM continent;''')
                continent_ids = [continent_id[0] for continent_id in cursor]
                if country[3] not in continent_ids:
                    yield SaveCountryFailedEvent('Invalid Continent ID')
                    raise sqlite3.Error

                # generates new country_id
                cursor = self.connection.execute(f'''SELECT country_id 
                                                     FROM country 
                                                     ORDER BY country_id DESC;''')
                country[0] = cursor.fetchone()[0] + 1

                # inserts new country
                country = tuple(country)
                self.connection.execute(f'''INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) 
                                            VALUES {country};''')
                yield CountrySavedEvent(Country(*country))

            except sqlite3.Error:
                yield SaveCountryFailedEvent('Save Country Failed')

        elif isinstance(event, SaveCountryEvent):
            try:
                country = event.country()

                # checks for valid continent_id
                cursor = self.connection.execute(f'''SELECT continent_id 
                                                     FROM continent;''')
                continent_ids = [continent_id[0] for continent_id in cursor]
                if country[3] not in continent_ids:
                    yield SaveCountryFailedEvent('Invalid Continent ID')
                    raise sqlite3.Error

                # updates country
                self.connection.execute(f'''UPDATE country
                                            SET country_code = \'{country[1]}\',
                                                name = \'{country[2]}\',
                                                continent_id = {country[3]},
                                                wikipedia_link = \'{country[4]}\',
                                                keywords = \'{country[5]}\'
                                            WHERE country_id = {country[0]};''')
                yield CountrySavedEvent(country)
            except sqlite3.Error:
                yield SaveCountryFailedEvent('Save Country Failed')

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
            cursor = self.connection.execute(f'''SELECT * 
                                                 FROM region {where_statement};''')
            for region in cursor:
                yield RegionSearchResultEvent(Region(*region))

        elif isinstance(event, LoadRegionEvent):
            # displays data of chosen region
            region_id = event.region_id()
            cursor = self.connection.execute(f'''SELECT * 
                                                 FROM region 
                                                 WHERE region_id = {region_id};''')
            yield RegionLoadedEvent(Region(*cursor.fetchone()))

        elif isinstance(event, SaveNewRegionEvent):
            try:
                region = list(event.region())

                # checks for valid continent_id
                cursor = self.connection.execute(f'''SELECT continent_id
                                                     FROM continent;''')
                continent_ids = [continent_id[0] for continent_id in cursor]
                if region[4] not in continent_ids:
                    yield SaveRegionFailedEvent('Invalid Continent ID')
                    raise sqlite3.Error

                # checks for valid country_id
                cursor = self.connection.execute(f'''SELECT country_id
                                                     FROM country;''')
                country_ids = [country_id[0] for country_id in cursor]
                if region[5] not in country_ids:
                    yield SaveRegionFailedEvent('Invalid Country ID')
                    raise sqlite3.Error

                # checks that country matches continent
                cursor = self.connection.execute(f'''SELECT continent_id, country_id
                                                     FROM country
                                                     WHERE continent_id = {region[4]} AND country_id = {region[5]};''')
                if not cursor.fetchone():
                    yield SaveRegionFailedEvent('Country Not In Continent')
                    raise sqlite3.Error

                # generates new region_id
                cursor = self.connection.execute('''SELECT region_id 
                                                    FROM region 
                                                    ORDER BY region_id DESC;''')
                region[0] = cursor.fetchone()[0] + 1

                # inserts new region
                region = tuple(region)
                self.connection.execute(f'''INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) 
                                            VALUES {region};''')
                yield RegionSavedEvent(Region(*region))

            except sqlite3.Error:
                yield SaveRegionFailedEvent('Save Region Failed')

        elif isinstance(event, SaveRegionEvent):
            try:
                region = event.region()

                # checks for valid continent_id
                cursor = self.connection.execute(f'''SELECT continent_id
                                                     FROM continent;''')
                continent_ids = [continent_id[0] for continent_id in cursor]
                if region[4] not in continent_ids:
                    yield SaveRegionFailedEvent('Invalid Continent ID')
                    raise sqlite3.Error

                # checks for valid country_id
                cursor = self.connection.execute(f'''SELECT country_id
                                                     FROM country;''')
                country_ids = [country_id[0] for country_id in cursor]
                if region[5] not in country_ids:
                    yield SaveRegionFailedEvent('Invalid Country ID')
                    raise sqlite3.Error

                # checks that country matches continent
                cursor = self.connection.execute(f'''SELECT continent_id, country_id
                                                     FROM country
                                                     WHERE continent_id = {region[4]} AND country_id = {region[5]};''')
                if not cursor.fetchone():
                    yield SaveRegionFailedEvent('Country Not In Continent')
                    raise sqlite3.Error

                # updates country
                self.connection.execute(f'''UPDATE region
                                            SET region_code = \'{region[1]}\',
                                                local_code = \'{region[2]}\',
                                                name = \'{region[3]}\',
                                                continent_id = {region[4]},
                                                country_id = {region[5]},
                                                wikipedia_link = \'{region[6]}\',
                                                keywords = \'{region[7]}\'
                                            WHERE region_id = {region[0]};''')
                yield RegionSavedEvent(region)
            except sqlite3.Error:
                yield SaveRegionFailedEvent('Save Region Failed')