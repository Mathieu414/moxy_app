from dash_extensions.enrich import html, dcc, dash_table
from .local_analysis.TrendGraph import TrendGraph

LocalAnalysis = html.Div(
    [
        TrendGraph,
        html.Article(
            children=[
                html.H3(
                    "Valeurs moyenne de SMO2(%) et pentes(%/s)", className="center"
                ),
                dash_table.DataTable(
                    style_header={
                        "backgroundColor": "grey",
                        "lineHeight": "50px",
                    },
                    style_data={
                        "backgroundColor": "#181c25",
                        "lineHeight": "70px",
                    },
                    style_cell={
                        "textAlign": "center",
                        "font-family": "system-ui",
                        "color": "white",
                        "textOverflow": "ellipsis",
                        "overflow": "hidden",
                    },
                    merge_duplicate_headers=True,
                    style_as_list_view=True,
                    id="trend-data-table",
                    export_format="csv",
                ),
            ]
        ),
        dcc.Store(id="trend-parameters"),
    ],
    className="hide",
    id="local-analysis-div",
)
