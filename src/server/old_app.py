import datetime
import time

from flask import Flask, request, render_template

from src.data_classes.ConnectionResults import ConnectionResults
from src.data_classes.ConnectionQuery import ConnectionQuery
from src.solver.FloydSolver import FloydSolver
from src.alternative_solvers.BfsSolver import BfsConnectionSolver
from src.alternative_solvers.BfsSolverDataProvider import BfsSolverDataProvider
from src.data_provider.FloydDataProvider import FloydDataProvider

app = Flask(__name__)

bfs_data = BfsSolverDataProvider.load_data()
bfs_solver1 = BfsConnectionSolver(bfs_data, earliest_arrival_time=False, latest_departure_time=False)
bfs_solver2 = BfsConnectionSolver(bfs_data, earliest_arrival_time=True, latest_departure_time=False)
bfs_solver3 = BfsConnectionSolver(bfs_data, earliest_arrival_time=True, latest_departure_time=True)

floyd_data = FloydDataProvider.load_floyd_data()
floyd_solver = FloydSolver(floyd_data)

solvers = {
    'BfsSolver(False, False)': bfs_solver1,
    'BfsSolver(True, False)': bfs_solver2,
    'BfsSolver(True, True)': bfs_solver3,
    'FloydSolver': floyd_solver,
}


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/search')
def search():
    start_time = request.args.get('start_time')
    start_stop_name = request.args.get('start_stop_name')
    end_stop_name = request.args.get('end_stop_name')

    start_date = datetime.datetime.now().date()
    try:
        start_time = datetime.datetime.strptime(start_time, '%H:%M').time()
    except ValueError:
        return 'Nieprawidłowy format godziny odjazdu'

    query = ConnectionQuery(start_date, start_time, start_stop_name, end_stop_name)

    outputs = {}

    for solver_name, solver in solvers.items():
        t1 = time.time()
        results = solver.find_connections(query)
        results = [min(results, key=ConnectionResults.arrival_time)]
        t2 = time.time()
        time_elapsed = t2 - t1
        outputs[solver_name] = {
            'results': results,
            'time_elapsed': time_elapsed,
        }

    return render_template('results.html', outputs=outputs)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
