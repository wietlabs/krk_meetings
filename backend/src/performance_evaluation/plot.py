from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

plt.style.use('ggplot')
plt.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#1f77b4'])
format = 'pdf'


def plot_connection_solver_execution_time_hist(execution_time: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(execution_time, binwidth=0.1, kde=True, ax=ax)
    ax.set(xlabel='Czas wyszukiwania [s]',
           ylabel='Procent przetworzonych zapytań',
           xticks=range(7),
           yticks=np.arange(0, 60, step=10),
           xlim=(-0.5, 6.5))
    # ax.yaxis.set_major_formatter(PercentFormatter(len(execution_time)))
    return fig


def plot_connection_solver_execution_time_ecdf(execution_time: pd.Series) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.ecdfplot(execution_time, ax=ax)
    sns.rugplot(execution_time, lw=0.2, alpha=0.5, ax=ax)
    ax.set(xlabel='Czas wyszukiwania [s]',
           ylabel='Procent przetworzonych zapytań',
           xticks=range(10),
           xlim=(-0.5, 6.5),
           ylim=(-0.05, 1.05))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    return fig


def plot_connection_solver_execution_time_vs_distance(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=performance_df, x='distance_km', y='execution_time', ax=ax)
    ax.set(xlabel='Średnia liczba przesiadek',
           ylabel='Czas wyszukiwania [s]')
    return fig


def plot_meeting_solver_execution_time_by_participants_count(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(data=performance_df, x='participants_count', y='execution_time',
                linewidth=0.6, fliersize=3, ax=ax)
    ax.set(xlabel='Liczba uczestników',
           ylabel='Czas wyszukiwania [s]',
           xticks=range(4, 30, 5))
    return fig


def plot_sequence_solver_execution_time_by_stops_to_visit(performance_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    performance_df['execution_time_ms'] = performance_df['execution_time'] * 1e3
    sns.boxplot(data=performance_df, x='stops_count', y='execution_time_ms',
                linewidth=0.6, fliersize=3, ax=ax)
    ax.set(xlabel='Liczba przystanków',
           ylabel='Czas wyszukiwania [ms]',
           yscale='log')
    return fig


def generate_connection_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'connection_solver_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)

    execution_time = performance_df['execution_time']

    plot_connection_solver_execution_time_hist(execution_time) \
        .savefig(f'plots/connection_solver_execution_time_hist.{format}')
    plot_connection_solver_execution_time_ecdf(execution_time) \
        .savefig(f'plots/connection_solver_execution_time_ecdf.{format}')
    plot_connection_solver_execution_time_vs_distance(performance_df) \
        .savefig(f'plots/connection_solver_execution_time_vs_distance.{format}')


def generate_connection_solver_path_sum_plots():
    def plot_connection_solver_execution_time_vs_distance(performance_df: pd.DataFrame) -> plt.Figure:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.boxplot(data=performance_df, x='transfer_count', y='execution_time', ax=ax)
        ax.set(xlabel='Średnia liczba przesiadek',
               ylabel='Czas wyszukiwania [s]')
        return fig

    pickle_path = Path(__file__).parent / 'data' / 'connection_solver_path_sum_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)

    plot_connection_solver_execution_time_vs_distance(performance_df) \
        .savefig(f'plots/connection_solver_execution_time_path_sum.{format}')


def generate_meeting_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'meeting_solver_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)

    plot_meeting_solver_execution_time_by_participants_count(performance_df) \
        .savefig(f'plots/meeting_solver_execution_time_by_participants_count.{format}')


def generate_sequence_solver_plots():
    pickle_path = Path(__file__).parent / 'data' / 'sequence_solver_performance.pickle'
    performance_df = pd.read_pickle(pickle_path)

    plot_sequence_solver_execution_time_by_stops_to_visit(performance_df) \
        .savefig(f'plots/sequence_solver_execution_time_by_stops_count.{format}')


if __name__ == '__main__':
    Path('plots').mkdir(parents=True, exist_ok=True)
    # generate_connection_solver_plots()
    # generate_meeting_solver_plots()
    # generate_sequence_solver_plots()
    generate_connection_solver_path_sum_plots()
