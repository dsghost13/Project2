def get_record(event, geo_scope: str) -> list:
    if geo_scope == 'continent':
        return list(event.continent())
    elif geo_scope == 'country':
        return list(event.country())
    elif geo_scope == 'region':
        return list(event.region())


def invalid_widget_entries(record: list, geo_scope: str, connection) -> str | None:
    error_message = list()
    if geo_scope != 'continent':
        error_message.append(check_valid_id(record, geo_scope, 'continent', connection))
        if geo_scope == 'region':
            error_message.append(check_valid_id(record, geo_scope, 'country', connection))
        for error in error_message:
            if error:
                return error


def check_valid_id(record: list, geo_scope: str, geo_check: str, connection) -> str | None:
    cursor = connection.execute(f'''SELECT {geo_check}_id
                                    FROM {geo_check};''')
    geo_ids = [geo_id[0] for geo_id in cursor]
    cursor.close()

    check_columns = {'country': (3, -1), 'region': (4, 5)}
    geo_index = check_columns[geo_scope][0]
    if geo_check == 'country':
        geo_index = check_columns[geo_scope][1]

    if record[geo_index] not in geo_ids:
        return f'Invalid {geo_check} ID'


def handle_empty_widget_entries(record: list, geo_scope: str) -> tuple:
    null_columns = {'continent': (-1, -1), 'country': (5, -1), 'region': (6, 7)}
    null_first = null_columns[geo_scope][0]
    null_second = null_columns[geo_scope][1]

    for i in range(len(record)):
        if isinstance(record[i], str):
            if not record[i]:
                if i == null_first or i == null_second:
                    record[i] = 'NULL'
                else:
                    record[i] = '(unassigned)'
    return tuple(record)


def format_for_sql(record: list):
    for i in range(len(record)):
        if isinstance(record[i], str):
            if record[i] != 'NULL':
                record[i] = f'\'{record[i]}\''
        else:
            record[i] = str(record[i])