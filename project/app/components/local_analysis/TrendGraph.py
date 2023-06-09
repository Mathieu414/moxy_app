from dash import html, dcc

TrendGraph = html.Div(
    id="trend-graph-div",
    children=html.Article(
        children=[
            html.H2("Tendance locale", className="center"),
            dcc.Loading(
                dcc.Graph(
                    id="trend-chart",
                )
            ),
        ]
    ),
)
