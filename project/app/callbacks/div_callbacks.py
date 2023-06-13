from dash_extensions.enrich import html, dcc, Input, Output, callback, State, dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
import utils.functions as fc
import plotly.io as pio


def get_div_callbacks(page, debug=True):
    @page.callback(
        Output("div-hr", "children"),
        Input("test-choice", "value"),
        Input("filtered-data", "data"),
        Input("muscle-groups", "data"),
        Input("thresholds", "data"),
        Input("print-pdf", "n_clicks"),
    )
    def add_hr_graphs(value, data, muscle_groups, thresholds, p):
        print("--add-hr-graphs--")
        # For the printing style
        pio.templates["plotly_white"]["data"]["histogram2dcontour"][0]["colorscale"] = (
            [0, "white"],
            [1, "#636efa "],
        )
        pio.templates["plotly_dark_custom"]["data"]["histogram2dcontour"][0][
            "colorscale"
        ] = ([0, "#181c25"], [1, "#636efa "])

        if (value is not None) and (data is not None) and (value in data):
            data_filtered = pd.concat(data[value])
            if "HR[bpm]" in data_filtered.columns:
                children = [
                    html.H2(
                        "Desoxygénation musculaire en fonction du HR",
                        className="center",
                    )
                ]
                graphs = []
                for n in muscle_groups[value][0].keys():
                    # remove the nas and convert the df columns to numpy arrays
                    x_fit = data_filtered["HR[bpm]"].dropna().to_numpy()
                    y_fit = data_filtered[n].dropna().to_numpy()

                    px, py = fc.segments_fit(x_fit, y_fit, 4)

                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=data_filtered["HR[bpm]"],
                            y=data_filtered[n],
                            mode="markers",
                            showlegend=False,
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=px,
                            y=py,
                            mode="lines+text",
                            line_color="#ab63fa",
                            name="Tendance",
                            text=[round(num, 1) for num in px],
                            textposition="top right",
                        )
                    )
                    if thresholds[value][0] is not None:
                        fig.add_vline(
                            x=thresholds[value][0],
                            line_width=3,
                            line_dash="dash",
                            line_color="green",
                            name="Seuil 1",
                        )
                    if thresholds[value][1] is not None:
                        fig.add_vline(
                            x=thresholds[value][1],
                            line_width=3,
                            line_dash="dash",
                            line_color="yellow",
                            name="Seuil 2",
                        )

                    fig.update_layout(
                        showlegend=False,
                        xaxis=dict(showgrid=True, gridwidth=3),
                        yaxis=dict(showgrid=True, gridwidth=3),
                    )
                    graphs.append(
                        html.Div(
                            [
                                html.H4(n, className="center"),
                                dcc.Graph(id="hr-" + n, figure=fig),
                            ],
                            id="hr-charts-div",
                        )
                    )
                children.append(
                    html.Div(
                        children=graphs,
                        className="grid-display",
                        id="hr-graphs-div",
                    )
                )
                content = html.Article(children=children, className="wrapper")
                return content
            else:
                return None
        else:
            return None

    @page.callback(
        Output("div-table", "children"),
        Input("analytics", "data"),
        [State("test-choice", "value"), State("muscle-groups", "data")],
        prevent_initial_call=True,
    )
    def update_results_table(data, value, muscle_groups):
        if debug:
            print("--update_results_table--")
            print(data)
        if data is not None:
            df = pd.DataFrame(index=list(muscle_groups[value][0].values()))
            df["Groupes musculaires"] = list(muscle_groups[value][0].values())

            # fill with the threshold data
            if len(data[1]) > 0:
                print("Fill with thresholds values")
                for i, seuil in enumerate(data[1]):
                    if len(seuil) > 0:
                        df["Seuil" + str(i + 1)] = seuil

            # fill with the minimal data
            if len(data[0]) > 0:
                print("Fill with minimal values")
                df["Desoxygénation minimale"] = data[0]

            df = df.round(1)

            content2 = [
                html.H2("Valeurs de référence", className="center"),
                dash_table.DataTable(
                    df.to_dict("records"),
                    style_header={
                        "backgroundColor": "grey",
                        "lineHeight": "50px",
                    },
                    style_data={
                        "backgroundColor": "#181c25",
                        "lineHeight": "70px",
                    },
                    style_cell={
                        "textAlign": "center",
                        "font-family": "system-ui",
                        "color": "white",
                        "width": "{}%".format(100 / len(df.columns)),
                        "textOverflow": "ellipsis",
                        "overflow": "hidden",
                    },
                    style_cell_conditional=[
                        {
                            "if": {"column_id": "Groupes musculaires"},
                            "textAlign": "left",
                        }
                    ],
                    style_as_list_view=True,
                ),
            ]

            content = html.Article(children=content2)

            return content
        else:
            return None
