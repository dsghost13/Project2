# p2app/engine/utility_functions/event_utils.py
#
# ICS 33 Fall 2024
# Project 2: Learning to Fly
#
# Utility functions used by all events

from p2app.events.continents import Continent
from p2app.events.countries import Country
from p2app.events.regions import Region

def convert_namedtuple(records: tuple | list, geo_scope: str):
    """Converts a tuple to a namedtuple with the desired type"""
    namedtuple_map = {'continent': Continent, 'country': Country, 'region': Region}
    converted_records = list()
    if isinstance(records, list):
        for record in records:
            converted_records.append(namedtuple_map[geo_scope](*record))
        return converted_records
    return [namedtuple_map[geo_scope](*records)]