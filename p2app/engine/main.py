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
        pass


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        #----------#
        # Database #
        #----------#

        if (isinstance(event, QuitInitiatedEvent)):
            yield EndApplicationEvent()

        elif (isinstance(event, OpenDatabaseEvent)):
            try:
                file_extension = os.path.splitext(event.path())[-1]
                if file_extension == '.db':
                    sqlite3.connect(event.path())
                    yield DatabaseOpenedEvent(event.path())
                else:
                    raise sqlite3.Error
            except sqlite3.Error:
                yield DatabaseOpenFailedEvent('Database Open Failed')

        #-------------#
        # Application #
        #-------------#

        elif (isinstance(event, CloseDatabaseEvent)):
            yield DatabaseClosedEvent()