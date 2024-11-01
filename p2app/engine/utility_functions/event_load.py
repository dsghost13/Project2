# p2app/engine/utility_functions/event_load.py
#
# ICS 33 Fall 2024
# Project 2: Learning to Fly
#
# Utility functions for loading-type events

from p2app.engine.utility_functions.event_utils import convert_namedtuple

def load_record(event, geo_scope: str, connection) -> tuple:
    """Loads record corresponding to the id given by the user"""
    record_id = get_record_id(event, geo_scope)
    matching_record = get_matching_record(record_id, geo_scope, connection)
    return matching_record


def get_record_id(event, geo_scope: str) -> int:
    """Gets id of requested record from the user"""
    if geo_scope == 'continent':
        return event.continent_id()
    elif geo_scope == 'country':
        return event.country_id()
    elif geo_scope == 'region':
        return event.region_id()


def get_matching_record(record_id: int, geo_scope: str, connection) -> tuple:
    """Gets record with a matching id"""
    cursor = connection.execute(f'''SELECT * 
                                    FROM {geo_scope} 
                                    WHERE {geo_scope}_id = {record_id};''')
    matching_record = convert_namedtuple(cursor.fetchone(), geo_scope)
    cursor.close()
    return matching_record