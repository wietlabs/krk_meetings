from static_map_module.GraphDataProvider import GraphDataProvider
from static_timetable_module.gtfs_static.DataProvider import DataProvider


if __name__ == "__main__":
    # extracted_data = DataProvider.load_data()
    # graph_data = GraphDataProvider.extract_data(extracted_data)
    graph_data = GraphDataProvider.load_data()
    print(graph_data.graph.edges[5, 154]['weight'])


