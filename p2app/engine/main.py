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
        self.cursor = None


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        #----------#
        # Database #
        #----------#

        if isinstance(event, QuitInitiatedEvent):
            try:
                self.cursor.close()
                yield EndApplicationEvent()
            except sqlite3.Error:
                yield ErrorEvent('End Application Failed')

        elif isinstance(event, OpenDatabaseEvent):
            try:
                # opens file if it's a database
                file_extension = os.path.splitext(event.path())[-1]
                if file_extension == '.db':
                    self.connection = sqlite3.connect(event.path())
                    self.cursor = self.connection.execute('PRAGMA foreign_keys = ON;')
                    yield DatabaseOpenedEvent(event.path())
                else:
                    raise sqlite3.Error('Not a Database File')

            except sqlite3.Error as e:
                if str(e):
                    yield DatabaseOpenFailedEvent(str(e))
                else:
                    yield DatabaseOpenFailedEvent('Open Database Failed')

        #-------------#
        # Application #
        #-------------#

        elif isinstance(event, CloseDatabaseEvent):
            try:
                self.cursor.close()
                yield DatabaseClosedEvent()
            except sqlite3.Error:
                yield ErrorEvent('Close Database Failed')

        #-----------#
        # Continent #
        #-----------#

        elif isinstance(event, StartContinentSearchEvent):
            try:
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
                self.cursor = self.connection.execute(f'''SELECT * 
                                                          FROM continent 
                                                          WHERE {where_statement};''')
                for continent in self.cursor:
                    yield ContinentSearchResultEvent(Continent(*continent))

            except sqlite3.Error:
                yield ErrorEvent('Corrupted Continent Search')

        elif isinstance(event, LoadContinentEvent):
            try:
                # displays data of chosen continent
                continent_id = event.continent_id()
                self.cursor = self.connection.execute(f'''SELECT * 
                                                          FROM continent 
                                                          WHERE continent_id = {continent_id};''')
                self.connection.commit()
                yield ContinentLoadedEvent(Continent(*self.cursor.fetchone()))

            except sqlite3.Error:
                yield ErrorEvent('Load Continent Failed')

        elif isinstance(event, SaveNewContinentEvent):
            try:
                continent = list(event.continent())

                # generates new continent_id
                self.cursor = self.connection.execute(f'''SELECT continent_id
                                                          FROM continent ORDER BY continent_id DESC;''')
                continent[0] = self.cursor.fetchone()[0] + 1

                # handles empty parameters
                for i in range(3):
                    if isinstance(continent[i], str):
                        if not continent[i]:
                            continent[i] = '(unassigned)'

                # inserts new continent
                continent = tuple(continent)
                self.connection.execute(f'''INSERT INTO continent (continent_id, continent_code, name) 
                                            VALUES {continent};''')
                self.connection.commit()
                yield ContinentSavedEvent(Continent(*continent))

            except sqlite3.Error:
                yield SaveContinentFailedEvent('Save Continent Failed')

        elif isinstance(event, SaveContinentEvent):
            try:
                continent = list(event.continent())

                # handles empty parameters
                for i in range(3):
                    if isinstance(continent[i], str):
                        if not continent[i]:
                            continent[i] = '(unassigned)'

                # updates continent
                continent = tuple(continent)
                self.connection.execute(f'''UPDATE continent
                                            SET continent_code = \'{continent[1]}\',
                                                name = \'{continent[2]}\'
                                            WHERE continent_id = {continent[0]};''')
                self.connection.commit()
                yield ContinentSavedEvent(Continent(*continent))

            except sqlite3.Error:
                yield SaveContinentFailedEvent('Save Continent Failed')

        #---------#
        # Country #
        #---------#

        elif isinstance(event, StartCountrySearchEvent):
            try:
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
                self.cursor = self.connection.execute(f'''SELECT * 
                                                          FROM country 
                                                          WHERE {where_statement};''')
                for country in self.cursor:
                    yield CountrySearchResultEvent(Country(*country))

            except sqlite3.Error:
                yield ErrorEvent('Corrupted Country Search')


        elif isinstance(event, LoadCountryEvent):
            try:
                # displays data of chosen country
                country_id = event.country_id()
                self.cursor = self.connection.execute(f'''SELECT * 
                                                          FROM country 
                                                          WHERE country_id = {country_id};''')
                yield CountryLoadedEvent(Country(*self.cursor.fetchone()))

            except sqlite3.Error:
                yield ErrorEvent('Load Country Failed')


        elif isinstance(event, SaveNewCountryEvent):
            try:
                country = list(event.country())

                # checks for valid continent_id
                self.cursor = self.connection.execute(f'''SELECT continent_id 
                                                          FROM continent;''')
                continent_ids = [continent_id[0] for continent_id in self.cursor]
                if country[3] not in continent_ids:
                    raise sqlite3.Error('Invalid Continent ID')

                # generates new country_id
                self.cursor = self.connection.execute(f'''SELECT country_id 
                                                          FROM country 
                                                          ORDER BY country_id DESC;''')
                country[0] = self.cursor.fetchone()[0] + 1

                # handles empty parameters
                for i in range(6):
                    if isinstance(country[i], str):
                        if not country[i]:
                            if i == 5:
                                country[i] = 'NULL'
                            else:
                                country[i] = '(unassigned)'
                country_tuple = tuple(country)

                # formats input values
                for i in range(6):
                    if isinstance(country[i], str):
                        if country[i] != 'NULL':
                             country[i] = f'\'{country[i]}\''
                    else:
                        country[i] = str(country[i])


                # inserts new country
                self.connection.execute(f'''INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) 
                                            VALUES ({', '.join(country)});''')
                self.connection.commit()
                yield CountrySavedEvent(Country(*country_tuple))

            except sqlite3.Error as e:
                if str(e):
                    yield SaveCountryFailedEvent(str(e))
                else:
                    yield SaveCountryFailedEvent('Save Country Failed')


        elif isinstance(event, SaveCountryEvent):
            try:
                country = list(event.country())

                # checks for valid continent_id
                self.cursor = self.connection.execute(f'''SELECT continent_id 
                                                          FROM continent;''')
                continent_ids = [continent_id[0] for continent_id in self.cursor]
                if country[3] not in continent_ids:
                    raise sqlite3.Error('Invalid Continent ID')

                # handles empty parameters
                for i in range(6):
                    if isinstance(country[i], str):
                        if not country[i]:
                            if i == 5:
                                country[i] = 'NULL'
                            else:
                                country[i] = '(unassigned)'
                country_tuple = tuple(country)

                # formats input values
                for i in range(6):
                    if isinstance(country[i], str):
                        if country[i] != 'NULL':
                            country[i] = f'\'{country[i]}\''
                    else:
                        country[i] = str(country[i])

                # updates country
                self.connection.execute(f'''UPDATE country
                                            SET country_code = {country[1]},
                                                name = {country[2]},
                                                continent_id = {country[3]},
                                                wikipedia_link = {country[4]},
                                                keywords = {country[5]}
                                            WHERE country_id = {country[0]};''')
                self.connection.commit()
                yield CountrySavedEvent(Country(*country_tuple))

            except sqlite3.Error as e:
                if str(e):
                    yield SaveCountryFailedEvent(str(e))
                else:
                    yield SaveCountryFailedEvent('Save Country Failed')


        #--------#
        # Region #
        #--------#

        elif isinstance(event, StartRegionSearchEvent):
            try:
                # gets entered parameters
                region_code = event.region_code()
                local_code = event.local_code()
                name = event.name()

                # scenario with all parameters entered
                columns = [region_code, local_code, name]
                params = [f'region_code = \'{region_code}\'',
                          f'local_code = \'{local_code}\'',
                          f'name = \'{name}\'']

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
                self.cursor = self.connection.execute(f'''SELECT * 
                                                          FROM region {where_statement};''')
                for region in self.cursor:
                    yield RegionSearchResultEvent(Region(*region))

            except sqlite3.Error:
                yield ErrorEvent('Corrupted Region Search')


        elif isinstance(event, LoadRegionEvent):
            try:
                # displays data of chosen region
                region_id = event.region_id()
                self.cursor = self.connection.execute(f'''SELECT * 
                                                          FROM region 
                                                          WHERE region_id = {region_id};''')
                yield RegionLoadedEvent(Region(*self.cursor.fetchone()))

            except sqlite3.Error:
                yield ErrorEvent('Load Region Failed')


        elif isinstance(event, SaveNewRegionEvent):
            try:
                region = list(event.region())

                # checks for valid continent_id
                self.cursor = self.connection.execute(f'''SELECT continent_id
                                                          FROM continent;''')
                continent_ids = [continent_id[0] for continent_id in self.cursor]
                if region[4] not in continent_ids:
                    raise sqlite3.Error('Invalid Continent ID')

                # checks for valid country_id
                self.cursor = self.connection.execute(f'''SELECT country_id
                                                          FROM country;''')
                country_ids = [country_id[0] for country_id in self.cursor]
                if region[5] not in country_ids:
                    raise sqlite3.Error('Invalid Country ID')

                # checks that country matches continent
                self.cursor = self.connection.execute(f'''SELECT continent_id, country_id
                                                          FROM country
                                                          WHERE continent_id = {region[4]} AND country_id = {region[5]};''')
                if not self.cursor.fetchone():
                    raise sqlite3.Error('Country Not In Continent')

                # generates new region_id
                self.cursor = self.connection.execute('''SELECT region_id 
                                                         FROM region 
                                                         ORDER BY region_id DESC;''')
                region[0] = self.cursor.fetchone()[0] + 1

                # handles empty parameters
                for i in range(8):
                    if isinstance(region[i], str):
                        if not region[i]:
                            if i == 6 or i == 7:
                                region[i] = 'NULL'
                            else:
                                region[i] ='(unassigned)'
                region_tuple = tuple(region)

                # formats input values
                for i in range(8):
                    if isinstance(region[i], str):
                        if region[i] != 'NULL':
                            region[i] = f'\'{region[i]}\''
                    else:
                        region[i] = str(region[i])

                # inserts new region
                self.connection.execute(f'''INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) 
                                            VALUES ({', '.join(region)});''')
                self.connection.commit()
                yield RegionSavedEvent(Region(*region_tuple))

            except sqlite3.Error as e:
                if str(e):
                    yield SaveRegionFailedEvent(str(e))
                else:
                    yield SaveRegionFailedEvent('Save Region Failed')


        elif isinstance(event, SaveRegionEvent):
            try:
                region = list(event.region())

                # checks for valid continent_id
                self.cursor = self.connection.execute(f'''SELECT continent_id
                                                          FROM continent;''')
                continent_ids = [continent_id[0] for continent_id in self.cursor]
                if region[4] not in continent_ids:
                    raise sqlite3.Error('Invalid Continent ID')

                # checks for valid country_id
                self.cursor = self.connection.execute(f'''SELECT country_id
                                                          FROM country;''')
                country_ids = [country_id[0] for country_id in self.cursor]
                if region[5] not in country_ids:
                    raise sqlite3.Error('Invalid Country ID')

                # checks that country matches continent
                self.cursor = self.connection.execute(f'''SELECT continent_id, country_id
                                                          FROM country
                                                          WHERE continent_id = {region[4]} AND country_id = {region[5]};''')
                if not self.cursor.fetchone():
                    raise sqlite3.Error('Country Not In Continent')

                # handles empty parameters
                for i in range(8):
                    if isinstance(region[i], str):
                        if not region[i]:
                            if i == 6 or i == 7:
                                region[i] = 'NULL'
                            else:
                                region[i] = '(unassigned)'
                region_tuple = tuple(region)

                # formats input values
                for i in range(8):
                    if isinstance(region[i], str):
                        if region[i] != 'NULL':
                            region[i] = f'\'{region[i]}\''
                    else:
                        region[i] = str(region[i])

                # updates country
                self.connection.execute(f'''UPDATE region
                                            SET region_code = {region[1]},
                                                local_code = {region[2]},
                                                name = {region[3]},
                                                continent_id = {region[4]},
                                                country_id = {region[5]},
                                                wikipedia_link = {region[6]},
                                                keywords = {region[7]}
                                            WHERE region_id = {region[0]};''')
                self.connection.commit()
                yield RegionSavedEvent(Region(*region_tuple))

            except sqlite3.Error as e:
                if str(e):
                    yield SaveRegionFailedEvent(str(e))
                else:
                    yield SaveRegionFailedEvent('Save Region Failed')