from enum import Enum


class ConnectionQuerySamples(Enum):
    krzeszowice_wolica = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Krzeszowice Dworzec Autobusowy', "end_stop_name": 'Wolica Most'}
    czarnowiejska_kleparz = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Czarnowiejska', "end_stop_name": 'Nowy Kleparz'}
    grunwaldzkie_kosciuszki = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Rondo Grunwaldzkie', "end_stop_name": 'Kopiec Kościuszki'}
    dunikowskoego_struga = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Dunikowskiego', "end_stop_name": 'Struga'}
    maki_pleszow = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Pleszów'}
    maki_kolorowe = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Czerwone Maki P+R',"end_stop_name": 'Os. Kolorowe'}
    walking_only = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Urząd Marszałkowski', "end_stop_name": 'Mazowiecka'}
    nightly_maki_biezanow = {"start_datetime": "2020-11-14 23:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Nowy Bieżanów P+R'}
    bad_start_stop_name = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'AAAAAA', "end_stop_name": 'Struga'}
    bad_end_stop_name = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Dunikowskiego' ,"end_stop_name": 'AAAAAA'}


class MeetingQuerySamples(Enum):
    square_3_stops = {"start_stop_names": ["Azory", "Kawiory", "Rondo Mogilskie"], "metric": "square"}
    bad_names = {"start_stop_names": ["AAAAA", "BBBBB", "Rondo Mogilskie"], "metric": "square"}


class SequenceQuerySamples(Enum):
    four_stops_to_fisit = {"start_stop_name": "Wrocławska", "end_stop_name": "AGH / UR", "stops_to_visit": ["Biprostal", "Kawiory", "Rondo Mogilskie", "Czarnowiejska"]}
    bad_stops_to_visit = {"start_stop_name": "Wrocławska", "end_stop_name": "AGH / UR", "stops_to_visit": ["AAAAAA", "Kawiory", "BBBBBB", "Czarnowiejska"]}
