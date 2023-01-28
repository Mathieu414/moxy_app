from dash import html, dcc, Input, Output, callback, State, dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import pages.utils.functions as fc


def get_div_callbacks(debug=True):
    @callback(
        Output('div-hr', 'children'),
        Input('test-choice', 'value'),
        Input('data-upload', 'data')
    )
    def add_hr_graphs(value, data):
        if (value is not None) and (data is not None):
            if len(data[value]) >= 4:
                for n in range(len(data[value][3])):
                    data[value][3][n] = pd.read_json(data[value][3][n])
                data_filtered = pd.concat(data[value][3])
                if "HR[bpm]" in data_filtered.columns:
                    children = [
                        html.H2("Desoxygénation musculaire en fonction du HR")]
                    for n in data[value][1]:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=data_filtered["HR[bpm]"],
                                                 y=data_filtered[n],
                                                 mode='markers',
                                                 showlegend=False))

                        fig.add_trace(go.Histogram2dContour(x=data_filtered["HR[bpm]"],
                                                            y=data_filtered[n],
                                                            colorscale=[
                                                                [0, '#141e26'], [1, '#636efa ']],
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
                        children.extend([html.H4(n),
                                        html.Div(
                            children=dcc.Graph(
                                        id="hr-" + n,
                                        figure=fig
                                        ),
                            className="card"
                        )]

                        )
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
         State("detect-filter", "value")],
        prevent_initial_call=True

    )
    def error_filter(n_clicks, stored_data, value, filter_value):
        if value is not None:
            if len(stored_data[value]) >= 3:
                data_selected = pd.read_json(stored_data[value][2])
                message = None
                print(filter_value)
                (result, message) = fc.cut_pauses(
                    data_selected, float(filter_value))
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
        if data:
            lines = []
            head = []
            body = []
            head = [html.Th("Groupes musculaires", scope="col")]

            for m in stored_data[value][1]:
                lines.append([html.Td(m)])

            # fill with the threshold data
            if len(data[1]) > 0:
                for i, seuil in enumerate(data[1]):
                    if len(seuil) > 0:
                        head.append(
                            html.Th(("Seuil " + str(i+1)), scope="col"))
                        for j in range(len(stored_data[value][1])):
                            lines[j].append(html.Td(round(seuil[j], 1)))

            # fill with the minimal data
            if len(data[0]) > 0:
                head.append(html.Th(("Desoxygénation minimale"), scope="col"))
                for j in range(len(data[0])):
                    lines[j].append(html.Td(round(data[0][j], 1)))

            if len(lines) > 0:
                for i in range(len(lines)):
                    body.append(html.Tr(lines[i]))

            content = html.Article(
                [html.H2("Valeurs de référence"),
                 html.Table(
                    [html.Thead(children=head),
                     html.Tbody(
                        body
                    )])]
            )

            return content
        else:
            return None

    @callback(
        Output("xml-div", "children"),
        [Input("vo2-data", "data")]
    )
    def display_xml(data):
        if data:
            data = pd.read_json(data)
            return dash_table.DataTable(
                data=data.to_dict('records'),
            )
