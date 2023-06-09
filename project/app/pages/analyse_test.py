from dash_extensions.enrich import (
    DashBlueprint,
    html,
    dcc,
    callback,
    Input,
    Output,
    ctx,
)
import plotly.io as pio
import plotly.graph_objects as go

from callbacks import (
    get_store_callbacks,
    get_figure_callbacks,
    get_dropdown_callbacks,
    get_threshold_callbacks,
    get_div_callbacks,
    get_p_callbacks,
    get_button_callbacks,
    get_modal_callbacks,
    get_datatable_callbacks,
)

from components import (
    PrintDialog,
    MuscleGroups,
    FullGraph,
    GlobalAnalysis,
    LocalAnalysis,
)

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
                    html.H1(children="Test VO2", id="title"),
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
            FullGraph,
            GlobalAnalysis,
            LocalAnalysis,
            PrintDialog,
            html.Button(className="hide", id="render", n_clicks=0),
            # dcc.Store stores the file data
            dcc.Loading(
                dcc.Store(id="raw-data", storage_type="session"),
                fullscreen=True,
                style={"backgroundColor": "transparent"},
                id="loading",
            ),
            dcc.Store(id="selected-data", storage_type="session"),
            dcc.Store(id="trend-data", storage_type="session"),
            dcc.Store(id="filtered-data", storage_type="session"),
            dcc.Store(id="muscle-groups", storage_type="session"),
            dcc.Store(id="analysis-type", storage_type="session"),
            dcc.Store(id="local-data", storage_type="session"),
            dcc.Store(id="thresholds", storage_type="session"),
            dcc.Store(id="peaks-parameters", storage_type="session"),
            dcc.Store(id="vo2-data", storage_type="session"),
            dcc.Store(id="analytics", storage_type="session"),
            dcc.Store(
                id="pio-template", data="plotly_dark_custom", storage_type="session"
            ),
            dcc.Location(id="refresh", refresh=True),
        ]
    )

    get_dropdown_callbacks(test_page, d)
    get_modal_callbacks(test_page, d)
    get_store_callbacks(test_page, d)
    get_figure_callbacks(test_page, d)
    get_threshold_callbacks(test_page, d)
    get_div_callbacks(test_page, d)
    get_p_callbacks(test_page, d)
    get_button_callbacks(test_page, d)
    get_datatable_callbacks(test_page, d)

    return test_page
