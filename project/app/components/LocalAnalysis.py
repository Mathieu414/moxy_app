from dash_extensions.enrich import html, dcc, dash_table
from .local_analysis.TrendGraph import TrendGraph

LocalAnalysis = html.Div(
    [
        TrendGraph,
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
                "width": "33%",
                "textOverflow": "ellipsis",
                "overflow": "hidden",
            },
            style_as_list_view=True,
            id="trend-data-table",
        ),
        dcc.Store(id="trend-parameters"),
    ],
    className="hide",
    id="local-analysis-div",
)
