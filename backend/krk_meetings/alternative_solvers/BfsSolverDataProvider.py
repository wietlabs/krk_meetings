from pathlib import Path

from krk_meetings.alternative_solvers.BfsSolverData import BfsSolverData
from krk_meetings.alternative_solvers.BfsSolverExtractor import BfsSolverExtractor
from krk_meetings.data_classes.ParsedData import ParsedData


class BfsSolverDataProvider:
    @staticmethod
    def prepare_data(parsed_data: ParsedData) -> None:
        extractor = BfsSolverExtractor()
        bfs_solver_data = extractor.extract(parsed_data)

        path = Path(__file__).parent.parent / 'data_provider' / 'data' / 'tmp' / 'bfs_solver_data.pickle'
        bfs_solver_data.save(path)

    @staticmethod
    def load_data() -> BfsSolverData:
        path = Path(__file__).parent.parent / 'data_provider' / 'data' / 'tmp' / 'bfs_solver_data.pickle'
        bfs_solver_data = BfsSolverData.load(path)
        return bfs_solver_data
