from static_map_module.GraphDataExtractor import GraphDataExtractor
from DataClasses.GraphData import GraphData
from pathlib import Path


class GraphDataProvider:
    @staticmethod
    def extract_data(gtfs_extracted_data):
        extractor = GraphDataExtractor()
        extracted_data = extractor.extract(gtfs_extracted_data)
        extracted_data.save(Path(__file__).parent / 'tmp' / 'graph_data.pickle')

        return extracted_data

    @staticmethod
    def load_data():
        extracted_data = GraphData.load(Path(__file__).parent / 'tmp' / 'graph_data.pickle')
        return extracted_data
