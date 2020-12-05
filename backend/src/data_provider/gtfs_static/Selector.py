from src.data_classes.ParsedData import ParsedData


class Selector:
    def select(self, parsed_data: ParsedData, *, service_id: int) -> ParsedData:
        calendar_df = parsed_data.calendar_df
        calendar_df_selected = parsed_data.calendar_df[calendar_df.index == service_id]

        calendar_dates_df = parsed_data.calendar_dates_df
        calendar_dates_df_selected = parsed_data.calendar_dates_df[calendar_dates_df['service_id'] == service_id]

        trips_df = parsed_data.trips_df
        trips_df_selected = trips_df.loc[trips_df.index.get_level_values(0) == service_id]

        stop_times_df = parsed_data.stop_times_df
        stop_times_df_selected = stop_times_df.loc[stop_times_df.index.get_level_values(0) == service_id]

        transfers_df = parsed_data.transfers_df
        transfers_df_selected = transfers_df.loc[transfers_df['service_id'] == service_id]

        return ParsedData(calendar_df=calendar_df_selected,
                          calendar_dates_df=calendar_dates_df_selected,
                          routes_df=parsed_data.routes_df,
                          trips_df=trips_df_selected,
                          stops_df=parsed_data.stops_df,
                          perons_df=parsed_data.perons_df,
                          stop_times_df=stop_times_df_selected,
                          transfers_df=transfers_df_selected)
