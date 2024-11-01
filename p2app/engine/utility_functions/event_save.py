# p2app/engine/utility_functions/event_save.py
#
# ICS 33 Fall 2024
# Project 2: Learning to Fly
#
# Utility functions for saving-type events
# Mostly specific to either inserting or updating
# Includes some important functions that cover both

from p2app.engine.utility_functions.save_utils import *

def insert_record(event, geo_scope: str, connection) -> str | tuple:
    """Inserts a new record in the database"""
    return save_record(event, 'insert', geo_scope, connection)


def update_record(event, geo_scope: str, connection) -> str | tuple:
    """Updates an existing record in the database"""
    return save_record(event, 'update', geo_scope, connection)


def save_record(event, mode: str, geo_scope: str, connection) -> str | tuple:
    """Saves changes to the database for inserting or updating records"""
    record = get_record(event, geo_scope)

    error_message = invalid_widget_entries(record, geo_scope, connection)
    if error_message:
        return error_message

    if mode == 'insert':
        generate_new_id(record, geo_scope, connection)
    record_tuple = handle_empty_widget_entries(record, geo_scope)
    format_for_sql(record)
    modify_table(mode, record, geo_scope, connection)
    return record_tuple


def generate_new_id(record: list, geo_scope: str, connection):
    """Generates a valid id for inserting a new record"""
    cursor = connection.execute(f'''SELECT {geo_scope}_id 
                                    FROM {geo_scope} 
                                    ORDER BY {geo_scope}_id DESC;''')
    recent_id = cursor.fetchone()[0]
    if recent_id:
        record[0] = recent_id + 1
    else:
        record[0] = 1
    cursor.close()


def modify_table(mode: str, record: list, geo_scope: str, connection):
    """Updates an existing record in the specified table"""
    parameters = {'continent': ['continent_id', 'continent_code', 'name'],
                  'country': ['country_id', 'country_code', 'name', 'continent_id', 'wikipedia_link', 'keywords'],
                  'region': ['region_id', 'region_code', 'local_code', 'name', 'continent_id', 'country_id', 'wikipedia_link', 'keywords']}

    if mode == 'insert':
        connection.execute(f'''INSERT INTO {geo_scope} ({', '.join(parameters[geo_scope])})
                               VALUES ({', '.join(record)});''')
    elif mode == 'update':
        set_statement = generate_set_statement(record, parameters[geo_scope])
        connection.execute(f'''UPDATE {geo_scope}
                               {set_statement}
                               WHERE {geo_scope}_id = {record[0]};''')
    connection.commit()


def generate_set_statement(record: list, parameters: list) -> str:
    """Generates a SQL SET statement for updating an existing record"""
    set_statement = 'SET'
    for i in range(1, len(record)):
        set_statement += f' {parameters[i]} = {record[i]},'
    return set_statement[:-1]