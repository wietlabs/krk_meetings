from pathlib import Path

from src.DataConverters.BasicDataExtractor import BasicDataExtractor
from src.DataConverters.Parser import Parser

if __name__ == '__main__':
    gtfs_dir_path = Path(__file__).parent / 'GTFS_KRK_T'

    parser = Parser()
    parsed_data = parser.parse(gtfs_dir_path)

    extractor = BasicDataExtractor()
    extracted_data = extractor.extract(parsed_data)
