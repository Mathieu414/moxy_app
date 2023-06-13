from dash import html, dcc
import plotly.graph_objects as go
import dash_mantine_components as dmc
from dash_iconify import DashIconify

FullGraph = html.Article(
    children=[
        html.Div(
            children=[
                html.Div(
                    [
                        html.H2(
                            "Selectionnez la zone du test",
                            className="center",
                        ),
                    ]
                ),
            ],
            className="row",
        ),
        dcc.Loading(
            html.Div(
                children=dcc.Graph(
                    id="test-chart", figure=go.Figure(), selectedData=None
                ),
                className="card",
            )
        ),
        html.Div(
            children=[
                html.Button(
                    children=[
                        dmc.Tooltip(
                            label="Analyse complète du test, avec une fonction de filtrage et de synchronisation avec la VO2",
                            children=[DashIconify(icon="carbon:information")],
                            multiline=True,
                            width=220,
                        ),
                        "Analyse globale",
                    ],
                    id="global-analysis-button",
                ),
                html.Button(
                    children=[
                        dmc.Tooltip(
                            label="Analyse d'un petite portion du test, avec des courbes de tendance pour chaque Moxy",
                            children=[DashIconify(icon="carbon:information")],
                            multiline=True,
                            width=220,
                        ),
                        "Analyse locale",
                    ],
                    id="local-analysis-button",
                ),
            ],
            className="grid",
        ),
        html.P(id="error-p-full-graph"),
    ],
    className="wrapper no-print",
)
