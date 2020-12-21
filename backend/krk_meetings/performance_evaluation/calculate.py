from pathlib import Path

import pandas as pd
from scipy import stats


def calculate_meeting_solver_execution_time_by_participants_count_r_squared() -> float:
    pickle_path = Path(__file__).parent / 'data' / 'meeting_solver_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)
    x = performance_df['participants_count']
    y = performance_df['execution_time'] * 1e3
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return r_value


if __name__ == '__main__':
    r_squared = calculate_meeting_solver_execution_time_by_participants_count_r_squared()
    print(f'R^2 = {r_squared:.4f}')
