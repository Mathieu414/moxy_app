from dash import html, dcc, Input, Output, callback
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm


def get_div_callbacks(debug=True):
    @callback(
        Output('div-hr', 'children'),
        Input('data-selection', 'data')
    )
    def add_graph(data):
        if data:
            data[0] = pd.read_json(data[0])
            if "HR[bpm]" in data[0].columns:
                children = [
                    html.H2("Desoxygénation musculaire en fonction du HR")]
                for n in data[1]:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data[0]["HR[bpm]"],
                                             y=data[0][n],
                                             mode='markers',
                                             showlegend=False))

                    fig.add_trace(go.Histogram2dContour(x=data[0]["HR[bpm]"],
                                                        y=data[0][n],
                                                        colorscale=[
                                                            [0, '#141e26'], [1, '#636efa ']],
                                                        showscale=False,
                                                        contours_showlines=False))
                    trendline = sm.nonparametric.lowess(data[0][n],
                                                        data[0]["HR[bpm]"],
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
