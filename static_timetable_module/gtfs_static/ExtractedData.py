import pandas as pd
from dataclasses import dataclass
from static_timetable_module.gtfs_static.Data import Data


@dataclass
class ExtractedData(Data):  # server has reference to its instance
    stops_df: pd.DataFrame
    transfers_trips_df: pd.DataFrame
    stop_times_trips_df: pd.DataFrame
    avg_durations_df: pd.DataFrame
    frequency_df: pd.DataFrame
