import networkx as nx

from src.data_provider.GtfsStaticDataProvider import GtfsStaticDataProvider

if __name__ == '__main__':
    # parsed_data = GtfsStaticDataProvider.prepare_data()
    parsed_data = GtfsStaticDataProvider.load_data()

    trips_df = parsed_data.trips_df
    stop_times_df = parsed_data.stop_times_df

    joined_df = stop_times_df.join(trips_df, on=['service_id', 'block_id', 'trip_num'])
    joined_df.reset_index(drop=True, inplace=True)
    joined_df = joined_df[['stop_id', 'route_id']]
    joined_df.drop_duplicates(inplace=True)

    G = nx.Graph()
    G.add_edges_from(
        (stop_id, -route_id)  # a simple trick to differentiate route nodes from stop nodes
        for stop_id, route_id in joined_df.to_numpy()
    )

    # for source_stop_id, target_stop_id in combinations(stops_df.index, 2):
    #     path_length = nx.shortest_path_length(G, source_stop_id, target_stop_id)
    #     min_number_of_changes = path_length // 2 - 1

    max_min_number_of_changes = nx.diameter(G) // 2 - 1  # each path looks like this: (stop)-(route)-(stop)-(route)-(stop)
    print(max_min_number_of_changes)
