from dash import html, dcc, Input, Output, callback, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import pages.utils.functions as fc
import datetime
import darkdetect
import plotly.io as pio


def get_div_callbacks(debug=True):
    @callback(
        Output('div-hr', 'children'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data'),
        State("seuils", "data")
    )
    def add_hr_graphs(value, data, seuils):
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
                                                            frac=0.5,
                                                            missing="drop")
                        fig.add_trace(go.Scatter(x=trendline[:, 0],
                                                 y=trendline[:, 1],
                                                 mode='lines',
                                                 line_color='#ab63fa',
                                                 name="Tendance",
                                                 line_shape='spline'))
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

    @callback(
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

    @callback(
        Output('div-table', "children"),
        Input("analytics", "data"),
        [State('data-upload', 'data'),
         State("test-choice", 'value')],
        prevent_initial_call=True
    )
    def update_results_table(data, stored_data, value):
        if debug:
            print("--update_results_table--")
        if data:
            lines = []
            head = []
            body = []

            lines2 = []
            head2 = []
            body2 = []

            head = [html.Th("Groupes musculaires", scope="col")]
            head2 = [html.Th("Groupes musculaires", scope="col")]

            for m in stored_data[value][1][0]:
                lines.append([html.Td(m)])
                lines2.append([html.Td(m)])

            # fill with the threshold data
            if len(data[1]) > 0:
                for i, seuil in enumerate(data[1]):
                    if len(seuil) > 0:
                        head.append(
                            html.Th(("Seuil " + str(i+1)), scope="col"))
                        for j in range(len(stored_data[value][1][0])):
                            lines[j].append(html.Td(round(seuil[j], 1)))

            # fill with the minimal data
            if len(data[0]) > 0:
                head.append(html.Th(("Desoxygénation minimale"), scope="col"))
                for j in range(len(data[0])):
                    lines[j].append(html.Td(round(data[0][j], 1)))

            # fill with the zones data
            if len(data[2]) > 0:
                for i, v in enumerate(data[2]):
                    if len(v) > 0:
                        head2.append(
                            html.Th(("Temps zone " + str(i + 1)), scope="col"))
                        for j, t in enumerate(v):
                            convert = str(datetime.timedelta(seconds=t))
                            lines2[j].append(html.Td(convert))

            if len(lines) > 0:
                for i in range(len(lines)):
                    body.append(html.Tr(lines[i]))

            if len(lines2) > 0:
                for i in range(len(lines2)):
                    body2.append(html.Tr(lines2[i]))

            content2 = [html.H2("Valeurs de référence", className="center"),
                        html.Table(
                [html.Thead(children=head),
                 html.Tbody(
                        body
                        )]),
            ]
            if len(data[2]) > 0:
                content2.extend([
                    html.H3("Temps dans les zones musculaires",
                            className="center"),
                    html.Table(
                        [html.Thead(children=head2),
                         html.Tbody(
                            body2
                        )])])

            content = html.Article(
                content2
            )

            return content
        else:
            return None
