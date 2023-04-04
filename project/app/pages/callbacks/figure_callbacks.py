from dash_extensions.enrich import Input, Output, callback
import pandas as pd
import pages.utils.figures as figures
import plotly.graph_objects as go


def get_figure_callbacks(page, debug=True):
    @ page.callback(
        Output('test-chart', 'figure'),
        Input('test-choice', 'value'),
        [Input("seuils", "data"),
         Input('data-upload', 'data')],
    )
    def update_graph(value, seuils, data):
        if debug:
            print("--update_graph--")
            print(value)
            print((data is None))
        if (value is not None) and (data is not None):
            print("value is not None")
            data = data[value]
            fig = figures.create_figure([data[0], data[1][0]])
            print("create figure :")
            return fig
        # if the value returns to None (selection is cleared)
        if ((value == 0) or (value is None)) and (data is not None):
            print("value is None")
            return go.Figure()
        else:
            return go.Figure()

    @ page.callback(
        Output('test-zoom-chart', 'figure'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def display_zoomed_data(value, data):
        if debug:
            print("--display_zoomed_data--")
        fig = go.Figure()
        if (value is not None) and (data is not None):
            if len(data[value]) >= 3:
                if debug:
                    print("create zoomed figure")
                fig = figures.create_figure(
                    [data[value][2], data[value][1][0]])
        return fig

    @ page.callback(
        Output('test-filter-chart', 'figure'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def display_filtered_data(value, data):
        fig = go.Figure()
        if (value is not None) and (data is not None):
            if len(data[value]) >= 4:
                if debug:
                    print("create filtered figure")
                fig = figures.create_filtered_figure(
                    [data[value][3], data[value][1]])
        return fig

    @ page.callback(
        Output('vo2-chart', 'figure'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def display_vo2_data(value, data):
        print("--update_vo2_graph--")
        fig = go.Figure()
        if (value is not None) and (data is not None):
            data = data[value]
            print("Longeur des données", len(data))
            if len(data) >= 4:
                if "VO2" in data[3][0].columns:
                    if debug:
                        print("create vo2 figure")
                    fig = figures.create_vo2_figure([data[3], data[1]])
        fig.update_layout(height=650)
        return fig
