from dash_extensions.enrich import html, dcc
from dash_iconify import DashIconify
from .global_analysis.ZoomedGraph import ZoomedGraph
from .global_analysis.FilteredGraph import FilteredGraph
from .global_analysis.VO2Upload import VO2Upload

GlobalAnalysis = html.Div(
    [
        VO2Upload,
        ZoomedGraph,
        FilteredGraph,
        # pagebreak for browser printing
        html.Div(className="pagebreak"),
        # table with informations, vo2 graph
        html.Div(
            [
                html.Div(id="div-table"),
                html.Article(
                    children=[
                        html.Div(html.H2("Courbe de la VO2", className="center")),
                        html.Div(
                            children=dcc.Loading(
                                dcc.Graph(
                                    id="vo2-chart",
                                )
                            ),
                            className="card",
                        ),
                    ],
                    className="wrapper",
                ),
                html.Div(className="pagebreak"),
                dcc.Loading(html.Div(id="div-hr"), id="hr-loading"),
            ],
        ),
        html.Button(
            [
                DashIconify(icon="carbon:printer"),
                html.B("Imprimer en PDF"),
            ],
            className="contrast outline",
            id="print-pdf",
        ),
    ],
    className="hide",
    id="global-analysis-div",
)
