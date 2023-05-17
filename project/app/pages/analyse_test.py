from dash_extensions.enrich import DashBlueprint, html, dcc
import plotly.io as pio
import plotly.graph_objects as go

from callbacks.store_callbacks import get_store_callbacks
from callbacks.figure_callbacks import get_figure_callbacks
from callbacks.dropdown_callbacks import get_dropdown_callbacks
from callbacks.inputs_callbacks import get_threshold_callbacks
from callbacks.div_callbacks import get_div_callbacks
from callbacks.p_callbacks import get_p_callbacks
from callbacks.button_callbacks import get_button_callbacks
from callbacks.modal_callbacks import get_modal_callbacks

from components.PrintDialog import PrintDialog
from components.MuscleGroups import MuscleGroups
from components.FullGraph import FullGraph
from components.ZoomedGraph import ZoomedGraph
from components.FilteredGraph import FilteredGraph

pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"]["layout"]["paper_bgcolor"] = "#141e26"
pio.templates["plotly_dark_custom"]["layout"]["plot_bgcolor"] = "#141e26"
pio.templates["plotly_dark_custom"]["layout"]["dragmode"] = "select"
pio.templates.default = "plotly_dark_custom"


def test_page():
    test_page = DashBlueprint()

    d = True

    print("\n")

    test_page.layout = html.Div(
        children=[
            # header
            html.Div(
                children=[
                    html.H1(
                        children="Test VO2",
                    ),
                    html.P(
                        children="Application pour analyser les données moxy d'un test VO2",
                    ),
                ],
                className="center",
                id="test-header-div",
            ),
            html.Article(
                children=[
                    html.H3("Selection du test"),
                    dcc.Dropdown(id="test-choice", placeholder="Selectionner le test"),
                ],
                className="menu no-print",
            ),
            # menu
            html.Article(
                children=[
                    html.P(html.B("1. Charger le fichier DataAverage.xlsx/.csv")),
                    dcc.Upload(
                        id="test-data-upload",
                        children=html.Button("Upload"),
                        className="inputs",
                    ),
                    html.Button(
                        "Effacer les données ",
                        className="contrast outline",
                        id="clear-button",
                        n_clicks=0,
                    ),
                ],
                className="menu no-print",
            ),
            MuscleGroups,
            # vo2 upload
            html.Article(
                children=[
                    html.P(html.B(id="vo2_p")),
                    dcc.Upload(
                        id="vo2-upload",
                        children=html.Button(
                            children="Upload",
                            id="vo2_button",
                            disabled=True,
                            className="secondary outline",
                        ),
                        multiple=False,
                        className="inputs",
                    ),
                ],
                className="menu no-print",
            ),
            html.Div(
                [FullGraph, ZoomedGraph, FilteredGraph],
                className="test-graphs-div",
            ),
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
                html.B("Imprimer en PDF"), className="contrast outline", id="print-pdf"
            ),
            PrintDialog,
            html.Button(className="hide", id="render", n_clicks=0),
            # dcc.Store stores the file data
            dcc.Loading(
                dcc.Store(id="data-upload", storage_type="session"),
                fullscreen=True,
                style={"backgroundColor": "transparent"},
                id="loading",
            ),
            dcc.Store(id="seuils", storage_type="session"),
            dcc.Store(id="peaks-parameters", storage_type="session"),
            dcc.Store(id="vo2-data", storage_type="session"),
            dcc.Store(id="analytics", storage_type="session"),
            dcc.Location(id="refresh", refresh=True),
        ]
    )

    get_modal_callbacks(test_page, d)
    get_figure_callbacks(test_page, d)
    get_dropdown_callbacks(test_page, d)
    get_threshold_callbacks(test_page, d)
    get_div_callbacks(test_page, d)
    get_p_callbacks(test_page, d)
    get_button_callbacks(test_page, d)
    get_store_callbacks(test_page, d)

    return test_page
