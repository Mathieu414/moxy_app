from dash import html, dcc

TrendGraph = html.Div(
    id="trend-graph-div",
    children=html.Article(
        children=[
            html.H2("Tendance locale", className="center"),
            dcc.Loading(
                dcc.Tabs(
                    id="trend-tabs",
                    parent_className="custom-tabs",
                )
            ),
        ]
    ),
)
