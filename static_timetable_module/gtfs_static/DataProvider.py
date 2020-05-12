from static_timetable_module.gtfs_static.Parser import Parser
from static_timetable_module.gtfs_static.Extractor import Extractor
from static_timetable_module.gtfs_static.ExtractedData import ExtractedData
from pathlib import Path


class DataProvider:
    @staticmethod
    def extract_data():
        parser = Parser()
        extractor = Extractor()
        parsed_data = parser.parse(Path(__file__).parent / 'GTFS_KRK_A')
        extracted_data = extractor.extract(parsed_data)
        extracted_data.save(Path(__file__).parent / 'tmp' / 'extracted_data.pickle')

        return extracted_data

    @staticmethod
    def load_data():
        extracted_data = ExtractedData.load(Path(__file__).parent / 'tmp' / 'extracted_data.pickle')
        return extracted_data
