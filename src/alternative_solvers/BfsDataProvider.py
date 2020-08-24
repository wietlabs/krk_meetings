from src.data_provider.Merger import Merger
from src.data_provider.Parser import Parser
from src.alternative_solvers.BfsSolverExtractor import BfsSolverExtractor
from src.alternative_solvers.BfsSolverData import BfsSolverData
from pathlib import Path

@staticmethod
def parse_and_extract_bfs_data():
    parser = Parser()
    parsed_data_A = parser.parse(Path(__file__).parent / 'data' / 'GTFS_KRK_A')
    parsed_data_T = parser.parse(Path(__file__).parent / 'data' / 'GTFS_KRK_T')

    merger = Merger()
    merged_data = merger.merge(parsed_data_A, parsed_data_T)

    extractor = BfsSolverExtractor()
    bfs_data = extractor.extract(merged_data)

    bfs_data.save(Path(__file__).parent / 'data' / 'tmp' / 'bfs_data.pickle')
    return bfs_data


@staticmethod
def load_bfs_data():
    bfs_data = BfsSolverData.load(Path(__file__).parent / 'data' / 'tmp' / 'bfs_data.pickle')
    return bfs_data
