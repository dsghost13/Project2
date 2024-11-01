from p2app.engine.utility_functions.event_utils import convert_namedtuple

def search_database(event, geo_scope: str, connection) -> list:
    widget_entries = get_widget_entries(event, geo_scope)
    where_statement = generate_where_statement(widget_entries)
    matching_records = get_matching_records(where_statement, geo_scope, connection)
    return matching_records


def get_widget_entries(event, geo_scope: str) -> dict:
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


def generate_where_statement(widget_entries: dict) -> str:
    where_statement = ''

    for widget in widget_entries.items():
        if widget[1]:
            if not where_statement:
                where_statement += f'WHERE {widget[0]} = \'{widget[1]}\''
            else:
                where_statement += f'AND {widget[0]} = \'{widget[1]}\''

    return where_statement


def get_matching_records(where_statement: str, geo_scope: str, connection) -> list:
    cursor = connection.execute(f'''SELECT * 
                                    FROM {geo_scope} 
                                    {where_statement};''')
    matching_records = convert_namedtuple(cursor.fetchall(), geo_scope)
    cursor.close()
    return matching_records