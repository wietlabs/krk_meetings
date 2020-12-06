from copy import deepcopy

import pandas as pd

from src.data_classes.ParsedData import ParsedData


class Corrector:
    names = {
        "Batalionu 'Skała' AK": 'Batalionu "Skała" AK',
        "Oczyszczalnia Ścieków 'Kujawy' (nż)": 'Oczyszczalnia Ścieków "Kujawy" (nż)',
        "Park 'Skały Twardowskiego' (nż)": 'Park "Skały Twardowskiego" (nż)',
        'Szpital Uniwersytecki / Instytut Pediatr': 'Szpital Uniwersytecki / Instytut Pediatrii',
    }

    def correct(self, parsed_data: ParsedData, copy: bool = True) -> ParsedData:
        if copy:
            parsed_data = deepcopy(parsed_data)

        parsed_data.stops_df = self._correct_stops_df(parsed_data.stops_df)
        parsed_data.perons_df = self._correct_perons_df(parsed_data.perons_df)

        return parsed_data

    def _correct_stops_df(self, stops_df: pd.DataFrame) -> pd.DataFrame:
        for original_name, corrected_name in self.names.items():
            stops_df.loc[stops_df['stop_name'] == original_name, 'stop_name'] = corrected_name
        return stops_df

    def _correct_perons_df(self, perons_df: pd.DataFrame) -> pd.DataFrame:
        for original_name, corrected_name in self.names.items():
            perons_df.loc[perons_df['peron_name'] == original_name, 'peron_name'] = corrected_name
        return perons_df
