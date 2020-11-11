from enum import Enum


class ConnectionQuerySamples(Enum):
    krzeszowice_wolica = {
        "start_datetime": "2020-05-24 12:00:00",
        "start_stop_name": 'Krzeszowice Dworzec Autobusowy',
        "end_stop_name": 'Wolica Most'
    }
    czarnowiejska_kleparz = {
        "start_datetime": "2020-05-24 12:00:00",
        "start_stop_name": 'Czarnowiejska',
        "end_stop_name": 'Nowy Kleparz'
    }
