from src.alternative_solvers.BfsSolverDataProvider import BfsSolverDataProvider
from src.data_provider.FloydDataProvider import DataProvider as FloydDataProvider
from src.data_provider.GtfsStaticDataProvider import GtfsStaticDataProvider

if __name__ == '__main__':
    # FloydDataProvider.parse_and_extract_floyd_data()

    GtfsStaticDataProvider.prepare_data()
    merged_data = GtfsStaticDataProvider.load_data()

    BfsSolverDataProvider.prepare_data(merged_data)
