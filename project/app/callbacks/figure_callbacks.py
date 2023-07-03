from dash_extensions.enrich import Input, Output, callback, State, dcc, ServersideOutput
import pandas as pd
import utils.figures as figures
import plotly.graph_objects as go


def get_figure_callbacks(page, debug=True):
    @page.callback(
        Output("test-chart", "figure"),
        [
            Input("test-choice", "value"),
            Input("thresholds", "data"),
            Input("muscle-groups", "data"),
            Input("pio-template", "data"),
        ],
        [
            State("raw-data", "data"),
        ],
    )
    def update_graph(value, thresholds, muscle_groups, p, raw_data):
        if debug:
            print("--update_graph--")
            print(value)
            print((raw_data is None))
            print(muscle_groups)
        if (value is not None) and (raw_data is not None):
            print("value is not None")
            fig = figures.create_figure(
                raw_data[value], muscle_groups[value][0], value, thresholds[value]
            )
            print("create figure :")
            return fig
        # if the value returns to None (selection is cleared)
        if ((value == 0) or (value is None)) and (raw_data is not None):
            print("value is None")
            return go.Figure()
        else:
            return go.Figure()

    @page.callback(
        Output("test-selected-chart", "figure"),
        [
            Input("test-choice", "value"),
            Input("selected-data", "data"),
            Input("muscle-groups", "data"),
            Input("thresholds", "data"),
            Input("pio-template", "data"),
            Input("analysis-type", "data"),
        ],
        prevent_initial_call=True,
    )
    def display_zoomed_data(
        value, selected_data, muscle_groups, thresholds, p, analysis_type
    ):
        if debug:
            print("--display_selected_data--")
        fig = go.Figure()
        if (
            (value is not None)
            and (selected_data is not None)
            and str(value) in analysis_type
            and analysis_type[str(value)] == "global-analysis-button"
        ):
            if debug:
                print("create zoomed figure")
            fig = figures.create_figure(
                selected_data[value], muscle_groups[value][0], value, thresholds[value]
            )
        return fig

    @page.callback(
        Output("test-filter-chart", "figure"),
        [
            Input("test-choice", "value"),
            Input("filtered-data", "data"),
            Input("muscle-groups", "data"),
            Input("thresholds", "data"),
            Input("pio-template", "data"),
            Input("analysis-type", "data"),
        ],
    )
    def display_filtered_data(
        value, filtered_data, muscle_groups, thresholds, p, analysis_type
    ):
        if debug:
            print("--display_filtered_data--")
            print(thresholds)
            print(analysis_type)
            print(value)
        fig = go.Figure()
        if (
            (value is not None)
            and (filtered_data is not None)
            and str(value) in analysis_type
            and analysis_type[str(value)] == "global-analysis-button"
        ):
            if value in filtered_data:
                if debug:
                    print("create filtered figure")
                fig = figures.create_filtered_figure(
                    filtered_data[value],
                    muscle_groups[value][0],
                    value,
                    thresholds[value],
                )
        return fig

    @page.callback(
        Output("vo2-chart", "figure"),
        Input("test-choice", "value"),
        Input("filtered-data", "data"),
        Input("muscle-groups", "data"),
        Input("vo2-data", "data"),
        Input("pio-template", "data"),
    )
    def display_vo2_data(value, data, muscle_groups, vo2_data, p):
        print("--update_vo2_graph--")
        fig = go.Figure()
        if (value is not None) and (data is not None):
            print("Longeur des données", len(data))
            if value in data:
                data = data[value]
                if "VO2" in data[0].columns:
                    if debug:
                        print("create vo2 figure")
                    fig = figures.create_vo2_figure(data, muscle_groups[value][0])
        fig.update_layout(height=650)
        return fig

    @page.callback(
        Output("trend-tabs", "children"),
        ServersideOutput("trend-parameters", "data"),
        [
            Input("test-choice", "value"),
            Input("trend-data", "data"),
            Input("muscle-groups", "data"),
            Input("pio-template", "data"),
            Input("analysis-type", "data"),
        ],
        State("trend-parameters", "data"),
        prevent_initial_call=True,
    )
    def display_trend_data(
        value, trend_data, muscle_groups, p, analysis_type, stored_trend_parameters
    ):
        if debug:
            print("--display_trend_data--")
            print(trend_data)
        fig = go.Figure()
        children = []
        if (
            (value is not None)
            and (trend_data is not None)
            and str(value) in analysis_type
            and analysis_type[str(value)] == "local-analysis-button"
        ):
            if debug:
                print("create trend figure")
            fig, parameters = figures.create_trend_figure(
                trend_data[value][0], muscle_groups[value][0]
            )
            children.append(
                dcc.Tab(
                    children=dcc.Graph(figure=fig),
                    label="Palier 1",
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                ),
            )
            columns = []
            for muscle in parameters[0]:
                columns.extend([(muscle, "%"), (muscle, "%/s")])
            mutli_col = pd.MultiIndex.from_tuples(columns)
            print(parameters[1])
            parameters_df = pd.DataFrame(
                [parameters[1]], index=["Palier 1"], columns=mutli_col
            )
            if len(trend_data[value]) > 1:
                for i, level in enumerate(trend_data[value][1:]):
                    fig, parameters = figures.create_trend_figure(
                        level, muscle_groups[value][0]
                    )
                    children.append(
                        dcc.Tab(
                            children=dcc.Graph(figure=fig),
                            label="Palier " + str(i + 2),
                            className="custom-tab",
                            selected_className="custom-tab--selected",
                        ),
                    )
                    parameters_df = parameters_df.append(
                        pd.Series(
                            parameters[1], index=mutli_col, name="Palier " + str(i + 2)
                        )
                    )
            if stored_trend_parameters is not None:
                stored_trend_parameters[value] = parameters_df
            else:
                stored_trend_parameters = {value: parameters_df}
        return children, stored_trend_parameters
