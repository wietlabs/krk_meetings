import pandas as pd
from dataclasses import dataclass
from DataClasses.Data import Data


@dataclass
class ExtractedData(Data):  # server has reference to its instance
    stops_df: pd.DataFrame
    transfers_df: pd.DataFrame
    stop_times_df: pd.DataFrame
    avg_durations_df: pd.DataFrame
    period_df: pd.DataFrame
    first_stops_df: pd.DataFrame
    routes_df: pd.DataFrame
    stops_df_by_name: pd.DataFrame
