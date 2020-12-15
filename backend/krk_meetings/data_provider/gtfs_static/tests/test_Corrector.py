import pandas as pd
from pandas.testing import assert_frame_equal

from krk_meetings.data_provider.gtfs_static.Corrector import Corrector


def test_correct_stops_df() -> None:
    stops_df = pd.DataFrame([
        ['Czerwone Maki P+R'],
        ["Batalionu 'Skała' AK"],
        ["Oczyszczalnia Ścieków 'Kujawy' (nż)"],
        ["Park 'Skały Twardowskiego' (nż)"],
        ['Szpital Uniwersytecki / Instytut Pediatr'],
    ], columns=['stop_name'])

    corrector = Corrector()
    actual_stops_df = corrector._correct_stops_df(stops_df)

    expected_stops_df = pd.DataFrame([
        ['Czerwone Maki P+R'],
        ['Batalionu "Skała" AK'],
        ['Oczyszczalnia Ścieków "Kujawy" (nż)'],
        ['Park "Skały Twardowskiego" (nż)'],
        ['Szpital Uniwersytecki / Instytut Pediatrii'],
    ], columns=['stop_name'])

    assert_frame_equal(actual_stops_df, expected_stops_df)


def test_correct_perons_df() -> None:
    perons_df = pd.DataFrame([
        ['Czerwone Maki P+R'],
        ["Batalionu 'Skała' AK"],
        ["Oczyszczalnia Ścieków 'Kujawy' (nż)"],
        ["Oczyszczalnia Ścieków 'Kujawy' (nż)"],
        ["Park 'Skały Twardowskiego' (nż)"],
        ["Park 'Skały Twardowskiego' (nż)"],
        ["Park 'Skały Twardowskiego' (nż)"],
        ['Szpital Uniwersytecki / Instytut Pediatr'],
        ['Szpital Uniwersytecki / Instytut Pediatr'],
        ['Szpital Uniwersytecki / Instytut Pediatr'],
        ['Szpital Uniwersytecki / Instytut Pediatr'],
    ], columns=['peron_name'])

    corrector = Corrector()
    actual_perons_df = corrector._correct_perons_df(perons_df)

    expected_perons_df = pd.DataFrame([
        ['Czerwone Maki P+R'],
        ['Batalionu "Skała" AK'],
        ['Oczyszczalnia Ścieków "Kujawy" (nż)'],
        ['Oczyszczalnia Ścieków "Kujawy" (nż)'],
        ['Park "Skały Twardowskiego" (nż)'],
        ['Park "Skały Twardowskiego" (nż)'],
        ['Park "Skały Twardowskiego" (nż)'],
        ['Szpital Uniwersytecki / Instytut Pediatrii'],
        ['Szpital Uniwersytecki / Instytut Pediatrii'],
        ['Szpital Uniwersytecki / Instytut Pediatrii'],
        ['Szpital Uniwersytecki / Instytut Pediatrii'],
    ], columns=['peron_name'])

    assert_frame_equal(actual_perons_df, expected_perons_df)
