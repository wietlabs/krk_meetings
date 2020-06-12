import datetime
import time

from flask import Flask, request, render_template

from DataClasses.TransferQuery import TransferQuery
from development.DataProviders.GraphDataProvider import GraphDataProvider
from development.DataProviders.GtfsStaticDataProvider import GtfsStaticDataProvider
from solvers.BfsSolver.BfsSolver import BfsSolver
from solvers.BfsSolver.BfsSolverData import BfsSolverData
from solvers.FloydSolver.FloydSolver import FloydSolver

app = Flask(__name__)

parsed_data = GtfsStaticDataProvider.load_parsed_data()
extracted_data = GtfsStaticDataProvider.load_extracted_data()

graph_data = GraphDataProvider.load_data()
floyd_solver = FloydSolver(graph_data)

bfs_solver_data = BfsSolverData.create(parsed_data, extracted_data)
bfs_solver = BfsSolver(bfs_solver_data)

solvers = [floyd_solver, bfs_solver]


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
    except:
        return 'Nieprawidłowy forma godziny odjazdu'

    query = TransferQuery(start_date, start_time, start_stop_name, end_stop_name)

    outputs = {}

    for solver in solvers:
        t1 = time.time()
        results = solver.find_connections(query)
        t2 = time.time()
        time_elapsed = t2 - t1

        solver_name = solver.__class__.__name__
        outputs[solver_name] = {
            'results': results,
            'time_elapsed': time_elapsed,
        }

    return render_template('results.html', outputs=outputs)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
