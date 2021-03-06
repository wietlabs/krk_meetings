from krk_meetings.data_provider.Downloader import Downloader
from krk_meetings.data_provider.gtfs_static.Corrector import Corrector
from krk_meetings.data_provider.gtfs_static.Merger import Merger
from krk_meetings.data_provider.gtfs_static.Parser import Parser

if __name__ == '__main__':
    downloader = Downloader()
    gtfs_zip_T, gtfs_zip_A = downloader.download_gtfs_static_data()

    parser = Parser()
    parsed_data_A = parser.parse(gtfs_zip_A)
    parsed_data_T = parser.parse(gtfs_zip_T)

    # selector = Selector()
    # selected_data_A = selector.select(parsed_data_A, service_id=1)
    # selected_data_T = selector.select(parsed_data_T, service_id=1)

    merger = Merger()
    merged_data, service_id_offset = merger.merge(parsed_data_A, parsed_data_T)

    corrector = Corrector()
    corrected_data = corrector.correct(merged_data)
