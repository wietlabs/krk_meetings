from pathlib import Path

from src.data_classes.ParsedData import ParsedData
from src.data_provider.Merger import Merger
from src.data_provider.Parser import Parser


class GtfsStaticDataProvider:
    @staticmethod
    def prepare_data() -> None:
        parser = Parser()

        with open(Path(__file__).parent / 'data' / 'GTFS_KRK_A.zip', 'rb') as f:
            parsed_data_A = parser.parse(f)

        with open(Path(__file__).parent / 'data' / 'GTFS_KRK_T.zip', 'rb') as f:
            parsed_data_T = parser.parse(f)

        merger = Merger()
        merged_data = merger.merge(parsed_data_A, parsed_data_T)

        path = Path(__file__).parent / 'data' / 'tmp' / 'merged_data.pickle'
        merged_data.save(path)

    @staticmethod
    def load_data() -> ParsedData:
        path = Path(__file__).parent / 'data' / 'tmp' / 'merged_data.pickle'
        merged_data = ParsedData.load(path)
        return merged_data
