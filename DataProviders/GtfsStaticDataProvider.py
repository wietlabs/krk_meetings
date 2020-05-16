from static_timetable_module.gtfs_static.Parser import Parser
from static_timetable_module.gtfs_static.Extractor import Extractor
from DataClasses.ExtractedData import ExtractedData
from pathlib import Path


class GtfsStaticDataProvider:
    @staticmethod
    def extract_data():
        parser = Parser()
        extractor = Extractor()
        parsed_data = parser.parse(Path(__file__).parent / 'GTFS_KRK_A')
        parsed_data.save(Path(__file__).parent / 'tmp' / 'parsed_data.pickle')
        extracted_data = extractor.extract(parsed_data)
        extracted_data.save(Path(__file__).parent / 'tmp' / 'extracted_data.pickle')

        return extracted_data

    @staticmethod
    def load_extracted_data():
        extracted_data = ExtractedData.load(Path(__file__).parent / 'tmp' / 'extracted_data.pickle')
        return extracted_data

    @staticmethod
    def parse_data():
        parser = Parser()
        parsed_data = parser.parse(Path(__file__).parent / 'GTFS_KRK_A')
        parsed_data.save(Path(__file__).parent / 'tmp' / 'parsed_data.pickle')
        return parsed_data

    @staticmethod
    def load_parsed_data():
        parsed_data = ExtractedData.load(Path(__file__).parent / 'tmp' / 'parsed_data.pickle')
        return parsed_data
