import pandas as pd
from dataclasses import dataclass
from GtfsStaticData import GtfsStaticData


@dataclass
class GtfsStaticParsedData(GtfsStaticData):  # server has reference to its instance
    calendar_df: pd.DataFrame
    routes_df: pd.DataFrame
    trips_df: pd.DataFrame
    stops_df: pd.DataFrame
    perons_df: pd.DataFrame
    stop_times_df: pd.DataFrame
    transfers_df: pd.DataFrame
