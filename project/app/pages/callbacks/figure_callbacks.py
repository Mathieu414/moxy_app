from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.io as pio
import pages.utils.figures as figures
import plotly.graph_objects as go


def get_figure_callbacks(debug=True):
    @ callback(
        Output('test-chart', 'figure'),
        Input('test-choice', 'value'),
        [Input("seuils", "data"),
         Input('data-upload', 'data')],
        prevent_initial_call=True
    )
    def update_graph(value, seuils, data):
        if debug:
            print("--update_graph--")
            print(value)
            print((data is None))
        if (value is not None) and (data is not None):
            print("value is not None")
            data = data[value]
            data[0] = pd.read_json(data[0])
            fig = figures.create_figure([data[0], data[1][0]])
            print("create figure :")
            return fig
        if (value == 0) and (data is None):
            print("value is None")
            return go.Figure()
        # {'layout': pio.templates["plotly_dark_custom"].layout}
        else:
            return go.Figure()

    @ callback(
        Output('test-zoom-chart', 'figure'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def display_zoomed_data(value, data):
        if debug:
            print("--display_zoomed_data--")
        fig = go.Figure()
        # fig = {'layout': pio.templates["plotly_dark_custom"].layout}
        if (value is not None) and (data is not None):
            if len(data[value]) >= 3:
                if debug:
                    print("create zoomed figure")
                data[value][2] = pd.read_json(data[value][2])
                fig = figures.create_figure(
                    [data[value][2], data[value][1][0]])
        return fig

    @ callback(
        Output('test-filter-chart', 'figure'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def display_filtered_data(value, data):
        fig = go.Figure()
        # fig = {'layout': pio.templates["plotly_dark_custom"].layout}
        if (value is not None) and (data is not None):
            if len(data[value]) >= 4:
                if debug:
                    print("create filtered figure")
                for n in range(len(data[value][3])):
                    data[value][3][n] = pd.read_json(data[value][3][n])
                fig = figures.create_filtered_figure(
                    [data[value][3], data[value][1]])
        return fig

    @ callback(
        Output('vo2-chart', 'figure'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def display_vo2_data(value, data):
        print("--update_vo2_graph--")
        fig = go.Figure()
        # fig = {'layout': pio.templates["plotly_dark_custom"].layout}
        if (value is not None) and (data is not None):
            data = data[value]
            print("Longeur des données", len(data))
            if len(data) >= 4:
                for n in range(len(data[3])):
                    data[3][n] = pd.read_json(data[3][n])
                if "VO2" in data[3][0].columns:
                    if debug:
                        print("create vo2 figure")
                    fig = figures.create_vo2_figure([data[3], data[1]])
        return fig
