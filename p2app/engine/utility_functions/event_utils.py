from p2app.events.continents import Continent
from p2app.events.countries import Country
from p2app.events.regions import Region

def convert_namedtuple(records: tuple | list, geo_scope: str):
    namedtuple_map = {'continent': Continent, 'country': Country, 'region': Region}
    converted_records = list()
    if isinstance(records, list):
        for record in records:
            converted_records.append(namedtuple_map[geo_scope](*record))
        return converted_records
    return [namedtuple_map[geo_scope](*records)]