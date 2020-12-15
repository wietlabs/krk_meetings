import pandas as pd


class VehiclePositionsMerger:
    def merge(self, vehicle_positions_df_1: pd.DataFrame, vehicle_positions_df_2: pd.DataFrame,
              services_id_offset: int) -> pd.DataFrame:
        vehicle_positions_df_2['service_id'] += services_id_offset
        vehicle_positions_df = pd.concat((vehicle_positions_df_1, vehicle_positions_df_2))
        return vehicle_positions_df
