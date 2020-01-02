import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import time
import datetime
import random


class Semaphore:
    def __init__(self, filename='semaphore.txt', f2="s2.txt"):
        self.filename = filename
        self.f2 = f2
        with open(self.filename, 'w') as f:
            f.write('done')

        with open(self.f2, 'w') as f:
            f.write('normal')

    def lock(self):
        with open(self.filename, 'w') as f:
            f.write('working')

    def unlock(self):
        with open(self.filename, 'w') as f:
            f.write('done')

    def stop(self):
        with open(self.f2, 'w') as f:
            f.write('stop')

    def start(self):
        with open(self.f2, 'w') as f:
            f.write('normal')

    def is_stopped(self):
        return open(self.f2, 'r').read() == 'stop'

    def is_locked(self):
        return open(self.filename, 'r').read() == 'working'


semaphore = Semaphore()

gyrox_data = []

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button('start', id='start'),
    html.Button('stop', id='stop'),

    html.Div(
        [html.H2('Spatial_Parameters2', style={'fontSize': 20, 'textAlign': 'center', }),
         dcc.Graph(id='stream1')], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,
                                          'width': '40%', 'display': 'inline-block', 'padding': '40 60'}),

    # html.Div(dcc.Input(id='input-box', type='text')),
    html.Div(id='state', children="enter value"),
    html.Div(id='stream_val', style={'display': 'none'}),
    # hidden signal value
    html.Div(id='signal', style={'display': 'none'}),
    dcc.Interval(id='graph_update', interval=6000, n_intervals=0)
])


def long_process():
    if semaphore.is_locked():
        return None
        # raise Exception('Resource is locked')
    semaphore.lock()
    time.sleep(5)
    semaphore.unlock()
    return random.randint(0, 10)

n_click_val = 0

@app.callback(
    Output('stream1', 'figure'),
    [Input('start', 'n_clicks'), Input('graph_update', 'n_intervals')])
def start_streaming(n_clicks, n_intervals):
    fig = go.Figure()
    print(n_clicks)
    if n_clicks:
        if not semaphore.is_stopped():
            val = long_process()
            if val:
                gyrox_data.append(val)
                fig.add_trace(go.Scatter(y=list(gyrox_data),
                                         name='Left', line_color='blue'))

                fig.update_traces(opacity=0.8)


    return fig


@app.callback(
    Output('state', 'children'),
    [Input('stop', 'n_clicks')])
def stop_streaming(n_clicks):
    state = ""
    if n_clicks:
        semaphore.stop()

    return state


if __name__ == '__main__':
    app.run_server(debug=True)
