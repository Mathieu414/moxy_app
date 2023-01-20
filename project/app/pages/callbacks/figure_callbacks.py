from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.io as pio
import pages.utils.functions as fc


def get_figure_callbacks(debug=True):
    @ callback(
        Output('test-chart', 'figure'),
        Input('test-choice', 'value'),
        State('data-upload', 'data'),
        prevent_initial_call=True
    )
    def update_graph(value, data):
        if debug:
            print("--update_graph--")
            print(value)
            print((data is None))
        if (value is not None) and (data is not None):
            print("value is not None")
            data = data[value]
            data[0] = pd.read_json(data[0])
            fig = fc.create_figure([data[0], data[1]])
            print("create figure :")
            return fig
        if (value == 0) and (data is None):
            print("value is None")
            return {'layout': pio.templates["plotly_dark_custom"].layout}
        else:
            raise PreventUpdate

    @ callback(
        Output('test-zoom-chart', 'figure'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def display_zoomed_data(value, data):
        fig = {'layout': pio.templates["plotly_dark_custom"].layout}
        if (value is not None) and (data is not None):
            if len(data[value]) >= 3:
                if debug:
                    print("create zoomed figure")
                data[value][2] = pd.read_json(data[value][2])
                fig = fc.create_figure([data[value][2], data[value][1]], False)
        return fig

    @ callback(
        Output('test-filter-chart', 'figure'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def display_filtered_data(value, data):
        fig = {'layout': pio.templates["plotly_dark_custom"].layout}
        if (value is not None) and (data is not None):
            if len(data[value]) >= 4:
                if debug:
                    print("create filtered figure")
                data[value][3] = pd.read_json(data[value][3])
                fig = fc.create_figure([data[value][3], data[value][1]], False)
        return fig
