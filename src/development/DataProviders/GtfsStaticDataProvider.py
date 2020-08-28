from pathlib import Path

from src.data_classes.ExtractedData import ExtractedData
from src.data_provider.Extractor import Extractor
from src.data_provider.Parser import Parser


class GtfsStaticDataProvider:
    @staticmethod
    def extract_data():
        parser = Parser()
        extractor = Extractor()
        parsed_data = parser.parse(Path(__file__).parent / 'data' / 'GTFS_KRK_A')
        parsed_data.save(Path(__file__).parent / 'tmp' / 'data' / 'parsed_data.pickle')
        extracted_data = extractor.extract(parsed_data)
        extracted_data.save(Path(__file__).parent / 'tmp' / 'data' / 'extracted_data.pickle')
        return extracted_data

    @staticmethod
    def load_extracted_data():
        extracted_data = ExtractedData.load(Path(__file__).parent / 'tmp' / 'data' / 'extracted_data.pickle')
        return extracted_data

    @staticmethod
    def parse_data():
        parser = Parser()
        parsed_data = parser.parse(Path(__file__).parent / 'data' / 'GTFS_KRK_A')
        parsed_data.save(Path(__file__).parent / 'tmp' / 'data' / 'parsed_data.pickle')
        return parsed_data

    @staticmethod
    def load_parsed_data():
        parsed_data = ExtractedData.load(Path(__file__).parent / 'data' / 'tmp' / 'parsed_data.pickle')
        return parsed_data
