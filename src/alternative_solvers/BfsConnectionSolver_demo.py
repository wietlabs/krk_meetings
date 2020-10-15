import time
from datetime import datetime
from pathlib import Path

from src.alternative_solvers.BfsConnectionSolver import BfsConnectionSolver
from src.alternative_solvers.BfsSolverExtractor import BfsSolverExtractor
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.data_provider.Merger import Merger
from src.data_provider.Parser import Parser

if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent / 'data_provider' / 'data'

    parser = Parser()
    parsed_data_A = parser.parse(data_dir / 'GTFS_KRK_A.zip')
    parsed_data_T = parser.parse(data_dir / 'GTFS_KRK_T.zip')

    merger = Merger()
    merged_data = merger.merge(parsed_data_A, parsed_data_T)

    extractor = BfsSolverExtractor()
    bfs_solver_data = extractor.extract(merged_data)

    # merged_data.save('merged_data.pickle')
    # bfs_solver_data.save('bfs_solver_data.pickle')

    # merged_data = ParsedData.load('merged_data.pickle')
    # bfs_solver_data = BfsSolverData.load('bfs_solver_data.pickle')

    solver = BfsConnectionSolver(bfs_solver_data,
                                 earliest_arrival_time=True,
                                 latest_departure_time=True,
                                 minimal_transfers_count=True)

    start_stop_id = 1362
    end_stop_id = 333
    start_dt = datetime(2020, 10, 14, 12, 34)

    query = ConnectionQuery(42, start_dt, start_stop_id, end_stop_id)

    t1 = time.time()
    connections = solver.find_connections(query)
    t2 = time.time()
    print(f'{t2 - t1:.3f} s')

    connection = connections[0]
    for transfer in connection.transfers:
        start_datetime = transfer.start_datetime
        end_datetime = transfer.end_datetime
        route_name = merged_data.routes_df.loc[transfer.route_id, 'route_short_name']
        start_stop_name = merged_data.stops_df.loc[transfer.start_stop_id, 'stop_name']
        end_stop_name = merged_data.stops_df.loc[transfer.end_stop_id, 'stop_name']
        print(f'{route_name} {start_datetime:%H:%M} {start_stop_name} -> {end_datetime:%H:%M} {end_stop_name}')
