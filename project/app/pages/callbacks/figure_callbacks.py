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
            fig = fc.create_figure(data)
            print("create figure :")
            return fig
        if (value == 0) and (data is None):
            print("value is None")
            return {'layout': pio.templates["plotly_dark_custom"].layout}
        else:
            raise PreventUpdate

    @ callback(
        Output('test-zoom-chart', 'figure'),
        Input('data-selection', 'data'),
    )
    def display_filtered_data(data):
        fig = {'layout': pio.templates["plotly_dark_custom"].layout}
        if data:
            if debug:
                print("create figure")
            data[0] = pd.read_json(data[0])
            fig = fc.create_figure(data)
        return fig

    @callback(
        Output("test-filter-chart", "figure"),
        Input("filter-selection-button", "n_clicks"),
        State("data-selection", "data"),
        prevent_initial_call=True
    )
    def filter_selection(n_clicks, data):
        if debug:
            print("--filter_selection--")
        if data:
            data[0] = pd.read_json(data[0])
            data[0] = fc.cut_df(data[0])
            fig = fc.create_figure(data, slope=False)
            return fig
