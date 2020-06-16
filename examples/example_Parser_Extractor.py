from pathlib import Path

from gtfs_static.Extractor import Extractor
from gtfs_static.Parser import Parser

if __name__ == '__main__':
    gtfs_dir_path = Path(__file__).parent / 'GTFS_KRK_T'

    parser = Parser()
    parsed_data = parser.parse(gtfs_dir_path)

    extractor = Extractor()
    extracted_data = extractor.extract(parsed_data)
    print(extracted_data.stops_df.sort_index())
