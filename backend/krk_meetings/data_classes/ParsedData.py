from dataclasses import dataclass

import pandas as pd

from krk_meetings.data_classes.Data import Data


@dataclass
class ParsedData(Data):
    calendar_df: pd.DataFrame
    calendar_dates_df: pd.DataFrame
    routes_df: pd.DataFrame
    trips_df: pd.DataFrame
    stops_df: pd.DataFrame
    perons_df: pd.DataFrame
    stop_times_df: pd.DataFrame
    transfers_df: pd.DataFrame
