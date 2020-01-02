import os
import copy
import time
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from flask_caching import Cache
import dash_daq as daq
from sample import add, rand


external_stylesheets = [
    # Dash CSS
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    'https://codepen.io/chriddyp/pen/brPBPO.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

N = 100

df = pd.DataFrame({
    'category': (
        (['apples'] * 5 * N) +
        (['oranges'] * 10 * N) +
        (['figs'] * 20 * N) +
        (['pineapples'] * 15 * N)
    )
})
df['x'] = np.random.randn(len(df['category']))
df['y'] = np.random.randn(len(df['category']))

gyrox_data = []

app.layout = html.Div([
    # dcc.Dropdown(
    #     id='dropdown',
    #     options=[{'label': i, 'value': i} for i in df['category'].unique()],
    #     value='apples'
    # ),

    html.Button('start', id='start'),
    html.Button('stop', id='stop'),

    # html.Div([
    #     html.Div(dcc.Graph(id='graph-1'), className="six columns"),
    #     html.Div(dcc.Graph(id='graph-2'), className="six columns"),
    # ], className="row"),
    # html.Div([
    #     html.Div(dcc.Graph(id='graph-3'), className="six columns"),
    #     html.Div(dcc.Graph(id='graph-4'), className="six columns"),
    # ], className="row"),
    #
    html.Div(
        [
            daq.PowerButton(
                id='start-recording',
                on=False,
                label='start recording',
                labelPosition='top'
            ),
            html.Div(id='status', style={'textAlign': 'center', 'marginBottom': 20})
        ]
    ),

    html.Div(
        [html.H2('Spatial_Parameters2', style={'fontSize': 20, 'textAlign': 'center', }),
         dcc.Graph(id='stream1')], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,
                                          'width': '40%', 'display': 'inline-block', 'padding': '40 60'}),

    #html.Div(dcc.Input(id='input-box', type='text')),
    html.Div(id='state', children="enter value"),
    html.Div(id='stream_val', style={'display': 'none'}),
    # hidden signal value
    html.Div(id='signal', style={'display': 'none'}),
    dcc.Interval(id='graph_update', interval=10000, n_intervals=0)
])


# perform expensive computations in this "global store"
# these computations are cached in a globally available
# redis memory store which is available across processes
# and for all time.
# @cache.memoize()
# def global_store(value):
#     # simulate expensive query
#     print('Computing value with {}'.format(value))
#     time.sleep(5)
#     return df[df['category'] == value]

result = None

def global_store2(command):
    result = rand.delay()
    if command == "stop":
        print("stop command received")
        result.revoke(terminate=True)
    while not result.ready():
        #print("loop")
        pass

    val = result.get()
    print(val)
    return val, command

def start_process(command):
    v, command = global_store2(command)

    return v


@app.callback([Output('signal', 'children'), Output('stream_val', 'children')],
              [Input('start', 'n_clicks'), Input('graph_update', 'n_intervals')])
def compute_value(n_clicks, value):
    # compute value and send a signal when done
    command = "none"
    v = "none"
    if n_clicks:
        v, command = global_store2(value)
    return command, v



@app.callback(
    Output('stream1', 'figure'),
    [Input('start', 'n_clicks'), Input('signal', 'children'), Input('stream_val', 'children')])
def start_streaming(n_clicks, command, stream_val):
    fig = go.Figure()
    print("stream_val: ", stream_val)
    if n_clicks and command != "stop":
        if not gyrox_data:
            print("gyrox_data empty")
            gyrox_data.append(start_process(2))
        else:
            if stream_val:
                gyrox_data.append(stream_val)
                fig.add_trace(go.Scatter(y=list(gyrox_data),
                                         name='Left', line_color='blue'))

                fig.update_traces(opacity=0.8)

    return fig


@app.callback(
    Output('state', 'children'),
    [Input('stop', 'n_clicks'), Input('signal', 'children')])
def stop_streaming(n_clicks, s):
    state = ""
    if n_clicks:
        try:
            start_process("stop")
            state = "stopped"
        except:
            pass


    return state





# @app.callback(Output('graph-1', 'figure'),
#               [Input('signal', 'children'), Input('graph_update', 'n_intervals')])
# def update_graph_1(value, n):
#     print(value)
#
#     return generate_figure(value, {
#         'data': [{
#             'type': 'scatter',
#             'mode': 'markers',
#             'marker': {
#                 'opacity': 0.5,
#                 'size': 14,
#                 'line': {'border': 'thin darkgrey solid'}
#             }
#         }]
#     })
#
#
# @app.callback(Output('graph-2', 'figure'), [Input('signal', 'children')])
# def update_graph_2(value):
#     return generate_figure(value, {
#         'data': [{
#             'type': 'scatter',
#             'mode': 'lines',
#             'line': {'shape': 'spline', 'width': 0.5},
#         }]
#     })
#
#
# @app.callback(Output('graph-3', 'figure'), [Input('signal', 'children')])
# def update_graph_3(value):
#     return generate_figure(value, {
#         'data': [{
#             'type': 'histogram2d',
#         }]
#     })
#
#
# @app.callback(Output('graph-4', 'figure'), [Input('signal', 'children')])
# def update_graph_4(value):
#     return generate_figure(value, {
#         'data': [{
#             'type': 'histogram2dcontour',
#         }]
#     })


if __name__ == '__main__':
    #app.run_server(debug=True, processes=6)
    app.run_server(debug=True)