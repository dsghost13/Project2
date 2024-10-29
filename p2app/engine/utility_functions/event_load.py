def load_record(event, geo_scope: str, connection) -> tuple:
    record_id = get_record_id(event, geo_scope)
    matching_record = get_matching_record(record_id, geo_scope, connection)
    return matching_record

def get_record_id(event, geo_scope: str) -> int:
    if geo_scope == 'continent':
        return event.continent_id()
    elif geo_scope == 'country':
        return event.country_id()
    elif geo_scope == 'region':
        return event.region_id()

def get_matching_record(record_id: int, geo_scope: str, connection) -> tuple:
    cursor = connection.execute(f'''SELECT * 
                                    FROM {geo_scope} 
                                    WHERE {geo_scope}_id = {record_id};''')
    matching_record = cursor.fetchone()
    cursor.close()
    return matching_record