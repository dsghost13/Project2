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
        self.event_map = {
                            QuitInitiatedEvent: [EndApplicationEvent, ErrorEvent('End Application Failed')],
                            OpenDatabaseEvent: [DatabaseOpenedEvent, DatabaseOpenFailedEvent],
                            CloseDatabaseEvent: [DatabaseClosedEvent, ErrorEvent('Close Database Failed')],

                            StartContinentSearchEvent: [ContinentSearchResultEvent, ErrorEvent('Corrupted Continent Search'), search_database, 'continent'],
                            LoadContinentEvent: [ContinentLoadedEvent, ErrorEvent('Load Continent Failed'), load_record, 'continent'],
                            SaveNewContinentEvent: [ContinentSavedEvent, SaveContinentFailedEvent, insert_record, 'continent'],
                            SaveContinentEvent: [ContinentSavedEvent, SaveContinentFailedEvent, update_record, 'continent'],

                            StartCountrySearchEvent: [CountrySearchResultEvent, ErrorEvent('Corrupted Country Search'), search_database, 'country'],
                            LoadCountryEvent: [CountryLoadedEvent, ErrorEvent('Load Country Failed'), load_record, 'country'],
                            SaveNewCountryEvent: [CountrySavedEvent, SaveCountryFailedEvent, insert_record, 'country'],
                            SaveCountryEvent: [CountrySavedEvent, SaveCountryFailedEvent, update_record, 'country'],

                            StartRegionSearchEvent: [RegionSearchResultEvent, ErrorEvent('Corrupted Region Search'), search_database, 'region'],
                            LoadRegionEvent: [RegionLoadedEvent, ErrorEvent('Load Region Failed'), load_record, 'region'],
                            SaveNewRegionEvent: [RegionSavedEvent, SaveRegionFailedEvent, insert_record, 'region'],
                            SaveRegionEvent: [RegionSavedEvent, SaveRegionFailedEvent, update_record, 'region']
                        }


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        try:
            # opens database
            if isinstance(event, OpenDatabaseEvent):
                file_extension = os.path.splitext(event.path())[-1]
                if file_extension == '.db':
                    self.connection = sqlite3.connect(event.path())
                    self.connection.execute('PRAGMA foreign_keys = ON;')
                    yield DatabaseOpenedEvent(event.path())
                else:
                    raise sqlite3.Error('Not a Database File')

            # closes database or exits GUI
            elif len(self.event_map[type(event)]) == 2:
                yield self.event_map[type(event)][0]()

            # GUI functionalities
            else:
                geo_scope = self.event_map[type(event)][3]
                result = self.event_map[type(event)][2](event, geo_scope, self.connection)
                if isinstance(result, str):
                    raise sqlite3.Error(result)
                for record in result:
                    yield self.event_map[type(event)][0](record)

        # catches defined failures and additional ErrorEvent failures
        except sqlite3.Error as e:
            if isinstance(self.event_map[type(event)][1], ErrorEvent):
                yield self.event_map[type(event)][1]
            else:
                yield self.event_map[type(event)][1](str(e))