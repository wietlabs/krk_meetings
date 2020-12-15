from enum import Enum


class ConnectionQuerySamples(Enum):
    krzeszowice_wolica = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Krzeszowice Dworzec Autobusowy', "end_stop_name": 'Wolica Most'}
    jubilat_baluckiego = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Jubilat', "end_stop_name": 'Bałuckiego (nż)'}
    jubilat_kostrze = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Jubilat', "end_stop_name": 'Kostrze Szkoła'}
    czarnowiejska_kleparz = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Czarnowiejska', "end_stop_name": 'Nowy Kleparz'}
    grunwaldzkie_kosciuszki = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Rondo Grunwaldzkie', "end_stop_name": 'Kopiec Kościuszki'}
    dunikowskoego_struga = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Dunikowskiego', "end_stop_name": 'Struga'}
    maki_pleszow = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Pleszów'}
    maki_kolorowe = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Czerwone Maki P+R',"end_stop_name": 'Os. Kolorowe'}
    maki_czarnowiejska = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Czerwone Maki P+R',"end_stop_name": 'Czarnowiejska'}
    brzeska_liberalow = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Brzeska (nż)',"end_stop_name": 'Libertów Działy (nż)'}
    walking_only = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Urząd Marszałkowski', "end_stop_name": 'Mazowiecka'}
    nightly_maki_biezanow_before_midnight = {"start_datetime": "2020-11-14 23:59:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Nowy Bieżanów P+R'}
    nightly_maki_biezanow_after_midnight = {"start_datetime": "2020-11-14 01:00:00", "start_stop_name": 'Czerwone Maki P+R', "end_stop_name": 'Nowy Bieżanów P+R'}
    bad_start_stop_name = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'AAAAAA', "end_stop_name": 'Struga'}
    bad_end_stop_name = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'Dunikowskiego' ,"end_stop_name": 'AAAAAA'}
    value_error = {"start_datetime": "2020-05-24 12:00:00", "start_stop_name": 'AGH / UR' ,"end_stop_name": 'Cechowa (nż)'}


class MeetingQuerySamples(Enum):
    square_3_stops = {"start_stop_names": ["Azory", "Kawiory", "Rondo Mogilskie"], "norm": "square"}
    bad_names = {"start_stop_names": ["AAAAA", "BBBBB", "Rondo Mogilskie"], "norm": "square"}


class SequenceQuerySamples(Enum):
    four_stops_to_fisit = {"start_stop_name": "Wrocławska", "end_stop_name": "AGH / UR", "stops_to_visit": ["Biprostal", "Kawiory", "Rondo Mogilskie", "Czarnowiejska"]}
    bad_stops_to_visit = {"start_stop_name": "Wrocławska", "end_stop_name": "AGH / UR", "stops_to_visit": ["AAAAAA", "Kawiory", "BBBBBB", "Czarnowiejska"]}


FAILING_CONNECTIONS = [
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Skalna (nż)', 'end_stop_name': 'Radziszów Zacisze (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Biskupińska (nż)', 'end_stop_name': 'Teatr Bagatela'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Zielonki Galicyjska (nż)', 'end_stop_name': 'Kryspinów'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Natansona', 'end_stop_name': 'Ochodza Staw (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Ochodza Dwór', 'end_stop_name': 'Węgrzce Centrum Medyczne (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Przykopy (nż)', 'end_stop_name': 'Pielgrzymowice Granica (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Sołtysowska Zakłady', 'end_stop_name': 'Konary Królowej Polski (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Forteczna', 'end_stop_name': 'Lubocza Szkoła'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Zabawa I (nż)', 'end_stop_name': 'Nielepice Pętla'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Zagórzyce Stare Owocowa (nż)', 'end_stop_name': 'Skawina Os.Radziszowskie (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Szpital Rydygiera', 'end_stop_name': 'Kamieńskiego Wiadukt (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Opolska Kładka', 'end_stop_name': 'Rzeszotary Zalesie (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Most Kotlarski (nż)', 'end_stop_name': 'Białucha'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Skawina Zachodnia (nż)', 'end_stop_name': 'Starego Wiarusa'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Judyma Szkoła', 'end_stop_name': 'Nowy Bieżanów P+R'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Walcownia (nż)', 'end_stop_name': 'Chmieleniec'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Urząd Skarbowy Nowa Huta', 'end_stop_name': 'Rżąka'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Uniwersytet Jagielloński', 'end_stop_name': 'Skawina Starostwo Powiatowe'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Kamień Szkoła', 'end_stop_name': 'Mydlniki Stawy (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Park Wodny', 'end_stop_name': 'Skrzyżowanie do Podchruścia (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Zelczyna Szkoła (nż)', 'end_stop_name': 'Balice Medweckiego (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Konopnickiej', 'end_stop_name': 'Libertów'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Zabierzów Młyn', 'end_stop_name': 'Zatyka (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Kostrze OSP', 'end_stop_name': 'Podłęże Balachówka (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Węgrzce Sudół (nż)', 'end_stop_name': 'Prokocim'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Zawiszy', 'end_stop_name': 'Kasztanowa'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Biskupa Prandoty', 'end_stop_name': 'Maciejowice Góra (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Ciekowiec (nż)', 'end_stop_name': 'Skawina Energetyków Przejazd PKP (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Os. Zielone', 'end_stop_name': 'Opolska Kładka'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Magazynowa (nż)', 'end_stop_name': 'Kryspinów'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Masłomiąca Staw (nż)', 'end_stop_name': 'Skawina Tyniecka Osiedle'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Przylasek Wyciąski (nż)', 'end_stop_name': 'Śliwiaka Zakłady'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Sieborowice (nż)', 'end_stop_name': 'Cholerzyn Skrzyżowanie (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Wieliczka Gdowska', 'end_stop_name': 'Będkowice Długa (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Chopina', 'end_stop_name': 'Archiwum UMK (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Balice Instytut Zootechniki (nż)', 'end_stop_name': 'Suchy Jar (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Ochmanów Oknoplast (nż)', 'end_stop_name': 'Pasternik (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Pszona', 'end_stop_name': 'Struga'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Os. Wandy', 'end_stop_name': 'Rudawa Osiedle (nż)'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Wola Batorska Zamoglice (nż)', 'end_stop_name': 'Sidzina'},
{'start_datetime': '2020-11-18 12:00:00', 'start_stop_name': 'Rynek Fałęcki', 'end_stop_name': 'Most Kotlarski (nż)'}
]
