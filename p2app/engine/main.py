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

from p2app.engine.utility_functions import *
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
            try:
                yield EndApplicationEvent()
            except sqlite3.Error:
                yield ErrorEvent('End Application Failed')

        elif isinstance(event, OpenDatabaseEvent):
            try:
                file_extension = os.path.splitext(event.path())[-1]
                if file_extension == '.db':
                    self.connection = sqlite3.connect(event.path())
                    self.connection.execute('PRAGMA foreign_keys = ON;')
                    yield DatabaseOpenedEvent(event.path())
                else:
                    raise sqlite3.Error('Not a Database File')
            except sqlite3.Error as e:
                yield DatabaseOpenFailedEvent(str(e))

        #-------------#
        # Application #
        #-------------#

        elif isinstance(event, CloseDatabaseEvent):
            try:
                yield DatabaseClosedEvent()
            except sqlite3.Error:
                yield ErrorEvent('Close Database Failed')

        #-----------#
        # Continent #
        #-----------#

        elif isinstance(event, StartContinentSearchEvent):
            try:
                matching_continents = search_database(event, 'continent', self.connection)
                for continent in matching_continents:
                    yield ContinentSearchResultEvent(Continent(*continent))
            except sqlite3.Error:
                yield ErrorEvent('Corrupted Continent Search')

        elif isinstance(event, LoadContinentEvent):
            try:
                continent = load_record(event, 'continent', self.connection)
                yield ContinentLoadedEvent(Continent(*continent))
            except sqlite3.Error:
                yield ErrorEvent('Load Continent Failed')

        elif isinstance(event, SaveNewContinentEvent):
            try:
                continent = save_record(event, 'insert', 'continent', self.connection)
                if isinstance(continent, str):
                    raise sqlite3.Error(continent)
                yield ContinentSavedEvent(Continent(*continent))
            except sqlite3.Error as e:
                yield SaveContinentFailedEvent(str(e))

        elif isinstance(event, SaveContinentEvent):
            try:
                continent = save_record(event, 'update', 'continent', self.connection)
                if isinstance(continent, str):
                    raise sqlite3.Error(continent)
                yield ContinentSavedEvent(Continent(*continent))
            except sqlite3.Error as e:
                yield SaveContinentFailedEvent(str(e))

        #---------#
        # Country #
        #---------#

        elif isinstance(event, StartCountrySearchEvent):
            try:
                matching_countries = search_database(event, 'country', self.connection)
                for country in matching_countries:
                    yield CountrySearchResultEvent(Country(*country))
            except sqlite3.Error:
                yield ErrorEvent('Corrupted Country Search')

        elif isinstance(event, LoadCountryEvent):
            try:
                country = load_record(event, 'country', self.connection)
                yield CountryLoadedEvent(Country(*country))
            except sqlite3.Error:
                yield ErrorEvent('Load Country Failed')

        elif isinstance(event, SaveNewCountryEvent):
            try:
                country = save_record(event, 'insert', 'country', self.connection)
                if isinstance(country, str):
                    raise sqlite3.Error(country)
                yield CountrySavedEvent(Country(*country))
            except sqlite3.Error as e:
                yield SaveCountryFailedEvent(str(e))

        elif isinstance(event, SaveCountryEvent):
            try:
                country = save_record(event, 'update', 'country', self.connection)
                if isinstance(country, str):
                    raise sqlite3.Error(country)
                yield CountrySavedEvent(Country(*country))
            except sqlite3.Error as e:
                yield SaveCountryFailedEvent(str(e))

        #--------#
        # Region #
        #--------#

        elif isinstance(event, StartRegionSearchEvent):
            try:
                matching_regions = search_database(event, 'region', self.connection)
                for region in matching_regions:
                    yield RegionSearchResultEvent(Region(*region))
            except sqlite3.Error:
                yield ErrorEvent('Corrupted Region Search')

        elif isinstance(event, LoadRegionEvent):
            try:
                region = load_record(event, 'region', self.connection)
                yield RegionLoadedEvent(Region(*region))
            except sqlite3.Error:
                yield ErrorEvent('Load Region Failed')

        elif isinstance(event, SaveNewRegionEvent):
            try:
                region = save_record(event, 'insert', 'region', self.connection)
                if isinstance(region, str):
                    raise sqlite3.Error(region)
                yield RegionSavedEvent(Region(*region))
            except sqlite3.Error as e:
                yield SaveRegionFailedEvent(str(e))

        elif isinstance(event, SaveRegionEvent):
            try:
                region = save_record(event, 'update', 'region', self.connection)
                if isinstance(region, str):
                    raise sqlite3.Error(region)
                yield RegionSavedEvent(Region(*region))
            except sqlite3.Error as e:
                yield SaveRegionFailedEvent(str(e))