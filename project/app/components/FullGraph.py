from dash import html, dcc
import plotly.graph_objects as go

FullGraph = html.Article(
    children=[
        html.Div(
            children=[
                html.Div(
                    [
                        html.H2(
                            "Courbe des groupes musculaires",
                            className="center",
                        ),
                    ]
                ),
            ],
            className="row",
        ),
        html.P(
            html.B("4. Selectionnez la zone du test"),
            className="no-print center",
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
                html.Button("Analyse globale", id="global-analysis-button"),
                html.Button("Analyse locale", id="local-analysis-button"),
            ],
            className="grid",
        ),
        html.P(id="error-p-full-graph"),
    ],
    className="wrapper no-print",
)
