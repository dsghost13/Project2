# p2app/engine/utility_functions/save_utils.py
#
# ICS 33 Fall 2024
# Project 2: Learning to Fly
#
# Utility functions for saving-type events
# Used in both inserting and updating

from p2app.engine.utility_functions.event_utils import convert_namedtuple

def get_record(event, geo_scope: str) -> list:
    """Gets record the user is attempting to insert or update"""
    if geo_scope == 'continent':
        return list(event.continent())
    elif geo_scope == 'country':
        return list(event.country())
    elif geo_scope == 'region':
        return list(event.region())


def invalid_widget_entries(record: list, geo_scope: str, connection) -> str | None:
    """Flags when the user attempts to pass invalid input"""
    error_message = list()
    if geo_scope != 'continent':
        error_message.append(check_valid_id(record, geo_scope, 'continent', connection))
        if geo_scope == 'region':
            error_message.append(check_valid_id(record, geo_scope, 'country', connection))
        for error in error_message:
            if error:
                return error


def check_valid_id(record: list, geo_scope: str, geo_check: str, connection) -> str | None:
    """Checks if the input id exists in the database"""
    cursor = connection.execute(f'''SELECT {geo_check}_id
                                    FROM {geo_check};''')
    geo_ids = [geo_id[0] for geo_id in cursor]
    cursor.close()

    check_columns = {'country': (3, -1), 'region': (4, 5)}
    geo_index = check_columns[geo_scope][0]
    if geo_check == 'country':
        geo_index = check_columns[geo_scope][1]

    if record[geo_index] not in geo_ids:
        return f'Invalid {geo_check.capitalize()} ID'


def handle_empty_widget_entries(record: list, geo_scope: str) -> tuple:
    """Assigns NULL to empty columns that allow NULL entries"""
    null_columns = {'continent': (-1, -1), 'country': (5, -1), 'region': (6, 7)}
    null_first = null_columns[geo_scope][0]
    null_second = null_columns[geo_scope][1]

    for i in range(len(record)):
        if isinstance(record[i], str):
            if not record[i]:
                if i == null_first or i == null_second:
                    record[i] = None
                else:
                    record[i] = '(unassigned)'
    return convert_namedtuple(tuple(record), geo_scope)