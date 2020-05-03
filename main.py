from static_map_module.ExtractedMap import ExtractedMap
from static_timetable_module.gtfs_static.DataProvider import DataProvider
from static_map_module.MapExtractor import MapExtractor
from pathlib import Path
import time

if __name__ == "__main__":
    """extracted_data = DataProvider.load_data()
    map_extractor = MapExtractor()
    start_time = time.time()
    extracted_map = map_extractor.extract_map(extracted_data)
    end_time = time.time()
    print("Time: ")
    print(end_time - start_time)
    extracted_map.save(Path(__file__).parent / 'tmp' / 'parsed_data.pickle')
    print(extracted_map.distances)"""

    map = ExtractedMap.load((Path(__file__).parent / 'tmp' / 'parsed_data.pickle'))
    print(map)
