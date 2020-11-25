from pathlib import Path

from src.data_provider.Merger import Merger
from src.data_provider.Parser import Parser
from src.data_provider.Selector import Selector

if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent / 'data_provider' / 'data'

    parser = Parser()
    parsed_data_A = parser.parse(data_dir / 'GTFS_KRK_A.zip')
    parsed_data_T = parser.parse(data_dir / 'GTFS_KRK_T.zip')

    selector = Selector()
    selected_data_A = selector.select(parsed_data_A, service_id=1)
    selected_data_T = selector.select(parsed_data_T, service_id=1)

    merger = Merger()
    merged_data, service_id_offset = merger.merge(selected_data_A, selected_data_T)
