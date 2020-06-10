from pathlib import Path

from gtfs_static.Parser import Parser

if __name__ == '__main__':
    gtfs_dir_path = Path(__file__).parent / 'GTFS_KRK_T'
    parser = Parser()
    parsed_data = parser.parse(gtfs_dir_path)
