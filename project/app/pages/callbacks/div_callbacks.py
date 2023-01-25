from dash import html, dcc, Input, Output, callback, State
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
                data_filtered = pd.read_json(data[value][3])
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
                errors = None
                if fc.cut_pauses(data_selected)[1] is not None:
                    errors = [html.P(fc.cut_pauses(data_selected, filter_value)[
                                     1], className="error")]
                if errors is not None:
                    return errors
                else:
                    raise PreventUpdate
            else:
                return html.P("Pas de données selectionnées", className="error")
        else:
            return html.P("Pas de test selectionné", className="error")
