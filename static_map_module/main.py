import time

from utils import *
from DataProviders.GraphDataProvider import GraphDataProvider
from DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.FloydSolver.FloydSover import FloydSolver

if __name__ == "__main__":
    extracted_data = GtfsStaticDataProvider.extract_data()
    routes_df = extracted_data.routes_df.set_index(['service_id', 'block_id', 'trip_num'])
    #graph_data = GraphDataProvider.extract_data(extracted_data)
    graph_data = GraphDataProvider.extract_data(extracted_data)

    solver = FloydSolver(graph_data)
    stops_df = graph_data.stops_df
    stops_df_by_name = stops_df.reset_index().set_index('stop_name')
    stop_times_df = graph_data.stop_times_df
    current_time = 6 * 3600

    start_stop = stops_df_by_name.loc['Czerwone Maki P+R']['stop_id']
    end_stop = stops_df_by_name.loc['Kombinat']['stop_id']

    results = None
    paths = solver.get_paths(start_stop, end_stop)
    start_time = time.time()
    for path in paths:
        results = solver.find_routes(path, current_time)
        if results is not None:
            for transfer in results:
                index, current_stop_id, next_stop_id, departure_time, arrival_time = transfer
                route_name = routes_df.loc[index]['route_name']
                current_stop_name = stops_df.loc[current_stop_id]['stop_name']
                next_stop_name = stops_df.loc[next_stop_id]['stop_name']
                print(route_name, ": ", current_stop_name, time_to_string(departure_time), "==>",
                      time_to_string(arrival_time), next_stop_name)
            print("------------------------------------")


















