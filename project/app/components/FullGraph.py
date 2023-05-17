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
            className="no-print",
        ),
        html.Div(
            id="inputs-threshold",
            children=[
                html.Div(
                    [
                        html.P("Seuil 1 (bpm)"),
                        dcc.Input(
                            id="seuil1",
                            type="number",
                            debounce=True,
                            disabled=True,
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.P("Seuil 2 (bpm)"),
                        dcc.Input(
                            id="seuil2",
                            type="number",
                            debounce=True,
                            disabled=True,
                        ),
                    ]
                ),
            ],
            className="grid",
        ),
        dcc.Loading(
            html.Div(
                children=dcc.Graph(id="test-chart", figure=go.Figure()),
                className="card",
            )
        ),
    ],
    className="wrapper no-print",
)
