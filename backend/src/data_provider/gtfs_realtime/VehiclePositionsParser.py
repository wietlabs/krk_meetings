from io import BytesIO
from pathlib import Path
from typing import Union

import pandas as pd
from google.transit import gtfs_realtime_pb2

from src.data_provider.data_provider_utils import parse_trip_id, parse_stop_id


class VehiclePositionsParser:
    def parse(self, path_or_buffer: Union[str, Path, BytesIO]) -> pd.DataFrame:
        if isinstance(path_or_buffer, BytesIO):
            return self._parse(path_or_buffer.getvalue())

        with open(path_or_buffer, 'rb') as f:
            return self._parse(f.read())

    def _parse(self, data) -> pd.DataFrame:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(data)
        feed_timestamp = feed.header.timestamp

        def gen():
            for entity in feed.entity:
                trip_id = entity.vehicle.trip.trip_id
                timestamp = entity.vehicle.timestamp
                # stop_id, peron_id = parse_stop_id(entity.vehicle.stop_id)
                stop_sequence = entity.vehicle.current_stop_sequence
                block_id, trip_num, service_id = parse_trip_id(trip_id)
                yield block_id, trip_num, service_id, stop_sequence, timestamp, feed_timestamp

        columns = ['block_id', 'trip_num', 'service_id', 'stop_sequence', 'timestamp', 'feed_timestamp']
        vehicle_positions_df = pd.DataFrame(gen(), columns=columns)
        # vehicle_positions_df.set_index(['block_id', 'trip_num', 'service_id'], inplace=True)
        return vehicle_positions_df
