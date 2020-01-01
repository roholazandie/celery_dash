import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from collections import deque
import dash_daq as daq
import time
from data import DataStream
from sample import model
import redis
import ast


app = dash.Dash('Example', external_stylesheets=[dbc.themes.DARKLY])
app.title = 'movement-data'
redis_instance = redis.StrictRedis.from_url('redis://localhost')

# datastream = DataStream()
#
# data = datastream.get()

from sample import model

model("")

times = []
gyrox_data = []


# def model(input_data):
#     time.sleep(2)
#     return [x*2 for x in input_data]


app.layout = html.Div([
    # html.Div(
    #     [
    #         daq.PowerButton(
    #             id='start-server',
    #             on=False,
    #             label='start server',
    #             labelPosition='top'
    #         ),
    #         html.Div(id='server-status', style={'textAlign': 'center', 'marginBottom': 20})
    #     ]
    # ),


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
            [html.H2('Spatial_Parameters2', style={'fontSize': 20, 'textAlign': 'center',}),
            dcc.Graph(id='stream1')], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,
                                              'width': '40%', 'display': 'inline-block', 'padding': '40 60'}),

    dcc.Interval(id='graph_update', interval=1000, n_intervals=0)

])


# @app.callback(
#     [Output('status', 'children'), Output('stream1', 'figure')],
#     [Input('start-recording', 'on'), Input('graph_update', 'n_intervals')])
# def update_output(on, graph_update):
#     fig = go.Figure()
#     if on:
#         for i, m_gyro_x in enumerate(data):
#             gyrox_data.append(m_gyro_x)
#
#             if i > 10:
#                 f = model.delay(gyrox_data)
#                 break
#         if f.ready():
#             print("dsdsd")
#             fig.add_trace(go.Scatter(y=list(f.get()),
#                                      name='Left', line_color='blue'))
#
#             fig.update_traces(opacity=0.8)
#
#     else:
#         pass
#
#     return 'The button is {}.'.format(on), fig



@app.callback(
    [Output('status', 'children'), Output('stream1', 'figure')],
    [Input('start-recording', 'on'), Input('graph_update', 'n_intervals')])
def update_output(on, graph_update):
    fig = go.Figure()
    if on:
        jsonified_df = redis_instance.hget("data", "dataset").decode("utf-8")
        jsonified_df = ast.literal_eval(jsonified_df)
        gyrox_data.extend(jsonified_df["a"])
        #print(gyrox_data)
        #print(gyrox_data)
        fig.add_trace(go.Scatter(y=list(gyrox_data),
                                 name='Left', line_color='blue'))

        fig.update_traces(opacity=0.8)

    else:
        pass

    return 'The button is {}.'.format(on), fig



if __name__ == "__main__":
    app.run_server(debug=True)