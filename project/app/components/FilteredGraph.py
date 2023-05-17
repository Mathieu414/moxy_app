from dash import html, dcc

FilteredGraph = html.Div(
    id="filter-data-div",
    children=html.Article(
        children=[
            html.H2("Courbe filtrée", className="center"),
            dcc.Loading(
                dcc.Graph(
                    id="test-filter-chart",
                )
            ),
        ]
    ),
)
