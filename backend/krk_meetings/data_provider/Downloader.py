from datetime import datetime
from ftplib import FTP
from io import BytesIO
from typing import Tuple


class Downloader:
    def get_last_update_time(self) -> datetime:
        with FTP('ztp.krakow.pl') as ftp:
            ftp.login()
            mtime_T = self._get_file_mtime(ftp, '/pliki-gtfs/GTFS_KRK_T.zip')
            mtime_A = self._get_file_mtime(ftp, '/pliki-gtfs/GTFS_KRK_A.zip')

        return max(mtime_A, mtime_T)

    def download_gtfs_static_data(self) -> Tuple[BytesIO, BytesIO]:
        gtfs_zip_T = BytesIO()
        gtfs_zip_A = BytesIO()

        with FTP('ztp.krakow.pl') as ftp:
            ftp.login()
            ftp.retrbinary('RETR /pliki-gtfs/GTFS_KRK_T.zip', gtfs_zip_T.write)
            ftp.retrbinary('RETR /pliki-gtfs/GTFS_KRK_A.zip', gtfs_zip_A.write)

        return gtfs_zip_T, gtfs_zip_A

    def download_vehicle_positions(self) -> Tuple[BytesIO, BytesIO]:
        vehicle_positions_pb_T = BytesIO()
        vehicle_positions_pb_A = BytesIO()

        with FTP('ztp.krakow.pl') as ftp:
            ftp.login()
            ftp.retrbinary('RETR /pliki-gtfs/VehiclePositions_T.pb', vehicle_positions_pb_T.write)
            ftp.retrbinary('RETR /pliki-gtfs/VehiclePositions_A.pb', vehicle_positions_pb_A.write)

        return vehicle_positions_pb_T, vehicle_positions_pb_A

    @staticmethod
    def _get_file_mtime(ftp: FTP, path: str) -> datetime:
        mtime_str = ftp.voidcmd('MDTM ' + path)[4:].strip()
        mtime_dt = datetime.strptime(mtime_str, '%Y%m%d%H%M%S')
        return mtime_dt
