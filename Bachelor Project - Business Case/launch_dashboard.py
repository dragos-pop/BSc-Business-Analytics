from flask import Flask, render_template, jsonify, request, abort
from datetime import datetime
import logging
import numpy as np
from model import utils
from model import model
import pandas as pd

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


class Handler:
    def __init__(self):
        self.request_list = []
        self.north_sea_queue = []

    def add_request(self, request):
        self.request_list.append(request)

    def arrival(self, ship):
        self.north_sea_queue.append(ship)


app = Flask(__name__)
request_handler = Handler()


@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    vals = []
    for j in range(1, 4):
        df, remainders, df_remainders = utils.generate_df('2020-01-10', 'input_files/normal_ships_model_input.csv', 7)
        colors = [tuple(np.random.uniform(0, 1, size=3)) for _ in range(len(df['NAME']))]
        obj, ship_name_to_duration = model.solve_linear_model(df=df, remainders=remainders, mtype=j,
                                                              objective_function=1, start='2020-01-10')
        vals.append(ship_name_to_duration)

    df = df[['MMSI', 'NAME', 'Draught', 'ETA', 'Width']]
    plot = utils.plotly_gantt_chart_model(df, df_remainders, '2020-01-10', 2.0, vals[0], colors, mtype=1)
    plot1 = utils.plotly_gantt_chart_model(df, df_remainders, '2020-01-10', 2.0, vals[1], colors, mtype=2)
    plot2 = utils.plotly_gantt_chart_model(df, df_remainders, '2020-01-10', 2.0, vals[2], colors, mtype=3)

    total_width = sum(df_remainders['Width'])

    df_remainders = df_remainders[['Berth', 'NAME', 'Start', 'Remaining', 'Width']]
    return render_template('layout.html', title='Data Harbour Dashboard', date='2020-01-10',
                           tables=[df.to_html(classes='data table')],
                           remainders=[df_remainders.to_html(classes='data table')], total_width=total_width,
                           graphJSON=plot, graphJSON1=plot1, graphJSON2=plot2)


@app.route('/harbour/api/v1.0/requests', methods=['POST'])
def add_requests():
    if not request.json or not 'name' in request.json:
        abort(400)
    req = {
        'id': len(request_handler.request_list) + 1,
        'name': request.json['name'],
        'mmsi': request.json['mmsi'],
        'terminal': request.json['terminal'],
        'customer': request.json['customer'],
        'cargo_type': request.json['cargo_type'],
        'cargo_quantity': request.json['cargo_quantity'],
        'time': datetime.now()
    }
    request_handler.add_request(req)
    return jsonify({'Message': "Successfully received request from {}".format(req['name'])}), 201


if __name__ == '__main__':
    app.run(debug=True)
