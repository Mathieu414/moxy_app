from dash import html, dcc, Input, Output, callback, State, dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import pages.utils.functions as fc
import datetime
import plotly.io as pio


def get_div_callbacks(debug=True):
    @callback(
        Output('div-hr', 'children'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def add_hr_graphs(value, data):
        # For the printing style
        pio.templates["plotly_white"]['data']['histogram2dcontour'][0]['colorscale'] = (
            [0, 'white'], [1, '#636efa '])
        pio.templates["plotly_dark_custom"]['data']['histogram2dcontour'][0]['colorscale'] = (
            [0, '#141e26'], [1, '#636efa '])

        if (value is not None) and (data is not None):
            if len(data[value]) >= 4:
                for n in range(len(data[value][3])):
                    data[value][3][n] = pd.read_json(data[value][3][n])
                data_filtered = pd.concat(data[value][3])
                if "HR[bpm]" in data_filtered.columns:
                    children = [
                        html.H2("Desoxygénation musculaire en fonction du HR", className="center")]
                    graphs = []
                    for n in data[value][1][0]:

                        # remove the nas and convert the df columns to numpy arrays
                        x_fit = data_filtered["HR[bpm]"].dropna().to_numpy()
                        y_fit = data_filtered[n].dropna().to_numpy()

                        px, py = fc.segments_fit(x_fit, y_fit, 4)

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=data_filtered["HR[bpm]"],
                                                 y=data_filtered[n],
                                                 mode='markers',
                                                 showlegend=False))

                        fig.add_trace(go.Histogram2dContour(x=data_filtered["HR[bpm]"],
                                                            y=data_filtered[n],
                                                            showscale=False,
                                                            contours_showlines=False))
                        trendline = sm.nonparametric.lowess(data_filtered[n],
                                                            data_filtered["HR[bpm]"],
                                                            frac=0.3,
                                                            missing="drop")
                        fig.add_trace(go.Scatter(x=px,
                                                 y=py,
                                                 mode='lines+text',
                                                 line_color='#ab63fa',
                                                 name="Tendance",
                                                 text=[round(num, 1)
                                                       for num in px],
                                                 textposition="top right"))
                        if "Seuil 1" in data_filtered.columns:
                            fig.add_vline(x=data_filtered["Seuil 1"][0], line_width=3, line_dash="dash",
                                          line_color="green", name="Seuil 1")
                        if "Seuil 2" in data_filtered.columns:
                            fig.add_vline(x=data_filtered["Seuil 2"][0], line_width=3, line_dash="dash",
                                          line_color="yellow", name="Seuil 2")

                        fig.update_layout(showlegend=False)
                        graphs.append(html.Div([html.H4(n, className="center"), dcc.Graph(
                            id="hr-" + n,
                            figure=fig)]))
                    children.append(
                        html.Div(children=graphs, className="grid-display"))
                    content = html.Article(children=children,
                                           className="wrapper"
                                           )
                    return content
                else:
                    raise PreventUpdate
            else:
                return None
        else:
            return None

    @ callback(
        Output('div-error-filter', 'children'),
        Input("filter-selection-button", "n_clicks"),
        [State("data-upload", 'data'),
         State("test-choice", 'value'),
         State("prominence", "value"),
         State("width", "value")],
        prevent_initial_call=True
    )
    def error_filter(n_clicks, stored_data, value, prominence, width):
        if value is not None:
            if len(stored_data[value]) >= 3:
                data_selected = pd.read_json(stored_data[value][2])
                message = None
                (result, message) = fc.cut_peaks(
                    data_selected, prominence=prominence, width=width)
                if message is not None:
                    if len(result) == 1:
                        return html.P(message, className="error")
                    if len(result) > 1:
                        return html.P(message, className="success")
                    else:
                        raise PreventUpdate
                else:
                    raise PreventUpdate
            else:
                return html.P("Pas de données selectionnées", className="error")
        else:
            return html.P("Pas de test selectionné", className="error")

    @ callback(
        Output('div-table', "children"),
        Input("analytics", "data"),
        [State('data-upload', 'data'),
         State("test-choice", 'value')],
        prevent_initial_call=True
    )
    def update_results_table(data, stored_data, value):
        if debug:
            print("--update_results_table--")
            print(data)
        if data:

            df = pd.DataFrame(index=stored_data[value][1][0])
            df["Groupes musculaires"] = stored_data[value][1][0]

            # fill with the threshold data
            if len(data[1]) > 0:
                print("Fill with thresholds values")
                for i, seuil in enumerate(data[1]):
                    if len(seuil) > 0:
                        df["Seuil" + str(i+1)] = seuil

            # fill with the minimal data
            if len(data[0]) > 0:
                print("Fill with minimal values")
                df["Desoxygénation minimale"] = data[0]

            df2 = pd.DataFrame()

            # fill with the zones data : only do if both tresholds are defined, i.e. if data[2] is full with data
            if len(data[2]) > 0:
                if (len(data[2][0]) != 0) and (len(data[2][1]) != 0) and (len(data[2][2]) != 0):
                    print("Fill with zones values")
                    df2["Groupes musculaires"] = stored_data[value][1][0]
                    time = [[] for i in range(len(data[2][0]))]
                    for i, v in enumerate(data[2]):
                        if len(v) > 0:
                            converts = []
                            for j, t in enumerate(v):
                                time[j].append(str(int(t/10)))
                                converts.append(
                                    str(datetime.timedelta(seconds=t)))
                            df2["Temps zone " + str(i + 1)] = converts
                    df2["Graph"] = [
                        "{" + ",".join(l) + "}" for l in time]

            df = df.round(1)

            content2 = [html.H2("Valeurs de référence", className="center"),
                        dash_table.DataTable(
                df.to_dict('records'),
                style_header={
                    'backgroundColor': 'grey',
                    'lineHeight': '50px',
                },
                style_data={
                    'backgroundColor': '#141e26',
                    'lineHeight': '70px',
                },
                style_cell={
                    'textAlign': 'center',
                    "font-family": "system-ui",
                    "color": "white",
                    'width': '{}%'.format(100/len(df.columns)),
                    'textOverflow': 'ellipsis',
                    'overflow': 'hidden'},
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'Groupes musculaires'},
                        'textAlign': 'left'
                    }
                ],
                style_as_list_view=True,)
            ]
            if len(data[2]) > 0:
                if (len(data[2][0]) != 0) and (len(data[2][1]) != 0) and (len(data[2][2]) != 0):
                    content2.extend([
                        html.H3("Temps dans les zones musculaires",
                                className="center"),
                        dash_table.DataTable(
                            df2.to_dict('records'),
                            style_header={
                                'backgroundColor': 'grey',
                                'lineHeight': '50px',
                            },
                            style_data={
                                'backgroundColor': '#141e26',
                                'lineHeight': '70px',
                            },
                            style_cell={
                                'textAlign': 'center',
                                "font-family": "system-ui",
                                "color": "white",
                                'width': '{}%'.format(100/len(df.columns)),
                                'textOverflow': 'ellipsis',
                                'overflow': 'hidden'},
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': 'Groupes musculaires'},
                                    'textAlign': 'left'
                                }
                            ],
                            style_data_conditional=[
                                {"if": {"column_id": "Graph"},
                                 "font-family": "Sparks-Bar-Wide",
                                 "font-size": 150}],
                            style_as_list_view=True,)
                    ])

            content = html.Article(children=content2
                                   )

            return content
        else:
            return None
