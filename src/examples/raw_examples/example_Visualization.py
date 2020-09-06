from src.data_provider.GtfsStaticDataProvider import GtfsStaticDataProvider
from src.development.Visualization import Visualization

if __name__ == '__main__':
    # extracted_data = GtfsStaticDataProvider.prepare_data()
    parsed_data = GtfsStaticDataProvider.load_data()

    visualization = Visualization()
    visualization.draw_stops(parsed_data)
    visualization.show()
