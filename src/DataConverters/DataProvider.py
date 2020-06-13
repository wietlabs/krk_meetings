from src.DataConverters.FloydDataExtractor import FloydDataExtractor
from src.DataClasses.FloydSolverData import FloydSolverData
from src.DataConverters.Parser import Parser
from src.DataConverters.BasicDataExtractor import BasicDataExtractor
from src.DataClasses.ExtractedData import ExtractedData
from pathlib import Path


class DataProvider:
    @staticmethod
    def extract_floyd_solver_data(extracted_data):
        extractor = FloydDataExtractor()
        floyd_solver_data = extractor.extract(extracted_data)
        floyd_solver_data.save(Path(__file__).parent / 'data' / 'tmp' / 'graph_data.pickle')
        return floyd_solver_data

    @staticmethod
    def load_floyd_solver_data():
        floyd_solver_data = FloydSolverData.load(Path(__file__).parent / 'data' / 'tmp' / 'graph_data.pickle')
        return floyd_solver_data

    @staticmethod
    def extract_data(parsed_data):
        extractor = BasicDataExtractor()
        extracted_data = extractor.extract(parsed_data)
        extracted_data.save(Path(__file__).parent / 'data' / 'tmp' / 'extracted_data.pickle')
        return extracted_data

    @staticmethod
    def load_extracted_data():
        extracted_data = ExtractedData.load(Path(__file__).parent / 'data' / 'tmp' / 'extracted_data.pickle')
        return extracted_data

    @staticmethod
    def parse_data():
        parser = Parser()
        parsed_data = parser.parse(Path(__file__).parent / 'data' / 'GTFS_KRK_A')
        parsed_data.save(Path(__file__).parent / 'data' / 'tmp' / 'parsed_data.pickle')
        return parsed_data

    @staticmethod
    def load_parsed_data():
        parsed_data = ExtractedData.load(Path(__file__).parent / 'data' / 'tmp' / 'parsed_data.pickle')
        return parsed_data
