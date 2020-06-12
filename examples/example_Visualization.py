from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from development.Visualization import Visualization

if __name__ == '__main__':
    # extracted_data = GtfsStaticDataProvider.extract_data()
    extracted_data = GtfsStaticDataProvider.load_extracted_data()

    visualization = Visualization()
    visualization.draw_stops(extracted_data)
    visualization.show()
