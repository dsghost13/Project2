# p2app/engine/utility_functions/event_searching.py
#
# ICS 33 Fall 2024
# Project 2: Learning to Fly
#
# Utility functions for searching-type events

from p2app.engine.utility_functions.event_utils import convert_namedtuple

def search_database(event, geo_scope: str, connection) -> list:
    """Searches database for record matching user-inputted constraints"""
    widget_entries = get_widget_entries(event, geo_scope)
    where_statement, entry_values = generate_where_statement(widget_entries)
    matching_records = get_matching_records(where_statement, entry_values, geo_scope, connection)
    return matching_records


def get_widget_entries(event, geo_scope: str) -> dict:
    """Gets user input(s) from the GUI"""
    widget_entries = dict()

    if geo_scope == 'continent':
        widget_entries['continent_code'] = event.continent_code()
    elif geo_scope == 'country':
        widget_entries['country_code'] = event.country_code()
    elif geo_scope == 'region':
        widget_entries['region_code'] = event.region_code()
        widget_entries['local_code'] = event.local_code()

    widget_entries['name'] = (event.name())
    return widget_entries


def generate_where_statement(widget_entries: dict) -> tuple:
    """Generates a SQL WHERE statement for searching records"""
    where_statement = ''
    entry_values = list()

    for widget, entry in widget_entries.items():
        if entry:
            if not where_statement:
                where_statement += f'WHERE {widget} = ? '
            else:
                where_statement += f'AND {widget} = ? '
            entry_values.append(entry)
    return where_statement, tuple(entry_values)


def get_matching_records(where_statement: str, entry_values: tuple, geo_scope: str, connection) -> list:
    """Gets record with a matching id"""
    cursor = connection.execute(f'''SELECT * 
                                    FROM {geo_scope}
                                    {where_statement};''', entry_values)
    matching_records = convert_namedtuple(cursor.fetchall(), geo_scope)
    cursor.close()
    return matching_records