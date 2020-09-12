from datetime import datetime
from ftplib import FTP
from io import BytesIO

from src.data_classes.ParsedData import ParsedData
from src.data_provider.Merger import Merger
from src.data_provider.Parser import Parser


class Downloader:
    def get_last_update_time(self) -> datetime:
        with FTP('ztp.krakow.pl') as ftp:
            ftp.login()
            mtime_T = self._get_file_mtime(ftp, '/pliki-gtfs/GTFS_KRK_T.zip')
            mtime_A = self._get_file_mtime(ftp, '/pliki-gtfs/GTFS_KRK_A.zip')

        return max(mtime_A, mtime_T)

    def download_merged_data(self) -> ParsedData:
        gtfs_zip_T = BytesIO()
        gtfs_zip_A = BytesIO()

        with FTP('ztp.krakow.pl') as ftp:
            ftp.login()
            ftp.retrbinary('RETR /pliki-gtfs/GTFS_KRK_T.zip', gtfs_zip_T.write)
            ftp.retrbinary('RETR /pliki-gtfs/GTFS_KRK_A.zip', gtfs_zip_A.write)

        parser = Parser()
        parsed_data_T = parser.parse(gtfs_zip_T)
        parsed_data_A = parser.parse(gtfs_zip_A)

        merger = Merger()
        merged_data = merger.merge(parsed_data_T, parsed_data_A)

        return merged_data

    @staticmethod
    def _get_file_mtime(ftp: FTP, path: str) -> datetime:
        mtime_str = ftp.voidcmd('MDTM ' + path)[4:].strip()
        mtime_dt = datetime.strptime(mtime_str, '%Y%m%d%H%M%S')
        return mtime_dt
