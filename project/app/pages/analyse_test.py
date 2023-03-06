import dash
from dash import html, dcc
import plotly.io as pio

from pages.callbacks.store_callbacks import get_store_callbacks
from pages.callbacks.figure_callbacks import get_figure_callbacks
from pages.callbacks.dropdown_callbacks import get_dropdown_callbacks
from pages.callbacks.inputs_callbacks import get_threshold_callbacks
from pages.callbacks.div_callbacks import get_div_callbacks
from pages.callbacks.p_callbacks import get_p_callbacks
from pages.callbacks.button_callbacks import get_button_callbacks
from pages.callbacks.modal_callbacks import get_modal_callbacks

dash.register_page(__name__)

pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"]['layout']['paper_bgcolor'] = '#141e26'
pio.templates["plotly_dark_custom"]['layout']['plot_bgcolor'] = '#141e26'
pio.templates["plotly_dark_custom"]['layout']['dragmode'] = 'select'
pio.templates.default = "plotly_dark_custom"

d = True

layout = html.Div(
    children=[

        # header
        html.Div(
            children=[
                html.H1(
                    children="Test VO2",),
                html.P(
                    children="Application pour analyser les données moxy d'un test VO2",
                ),
            ],
            className="center",
            id="test-header-div"
        ),

        # menu
        html.Article(children=[
            html.P(html.B(
                '1. Charger le fichier DataAverage.xlsx/.csv')),
            dcc.Upload(
                id='test-upload',
                children=html.Button(
                    'Upload')
            ),
            html.Button("Effacer les données ",
                        className="contrast outline", id="clear-button", n_clicks=0),
            dcc.Loading(dcc.Dropdown(
                id="test-choice"))],
            className="menu no-print",
        ),
        html.Article(children=[
            html.P(html.B("2.Définir les groupes musculaires")),
            html.Button(children='Définir', id="modal_open",
                        disabled=True, className="secondary outline"),
            html.Dialog(
                [
                    html.Article([html.H3("Définir les groupes musulaires"),
                                  html.Div(id="modal_content"),
                                  html.Footer(
                        html.Button("Confirmer", id="modal_close")
                    ),])
                ],
                id="modal",
                open=False
            ),],
            className="menu",
        ),
        html.Article(children=[
            html.P(html.B(id="vo2_p")),
            dcc.Upload(
                id='vo2-upload',
                children=html.Button(
                    children='Upload', id="vo2_button", disabled=True, className="secondary outline"),
                multiple=False
            )],
            className="menu no-print",
        ),
        html.Div(id="xml-div"),

        # graphs
        html.Div([
            html.Article(
                children=[
                    html.Div(children=[
                        html.Div(html.H2("Courbe des groupes musculaires"),
                             className="col-8"),
                    ], className="row"),
                    html.P(html.B("4. Selectionnez la zone du test")),
                    html.Div(id="inputs-threshold",
                             children=[
                                 html.Div([
                                     html.P("Seuil 1"),
                                     dcc.Input(
                                         id="seuil1", type='number', debounce=True, disabled=True)
                                 ]),
                                 html.Div([
                                     html.P("Seuil 2"),
                                     dcc.Input(
                                         id="seuil2", type='number', debounce=True, disabled=True)
                                 ])],
                             className='grid'),
                    dcc.Loading(html.Div(
                        children=dcc.Graph(
                            id="test-chart",
                            figure={
                                'layout':
                                pio.templates["plotly_dark_custom"].layout
                            }
                        ),
                        className="card"
                    ))

                ],
                className="wrapper"
            ),

            html.Div(className="pagebreak"),

            html.Div(id="zoom-chart-div", children=html.Article(children=[
                html.Div([html.H2("Courbe de la sélection")]),
                dcc.Loading(dcc.Graph(id="test-zoom-chart",
                                      figure={
                                          'layout':
                                          pio.templates["plotly_dark_custom"].layout
                                      })),
                html.Hr(),
                html.Div([
                    html.Div(html.P("Paramètres de detection des pauses:"),
                         className="col-sm-4"),
                ], className="row"),
                html.Div([
                    html.Div(html.Label(["Hauteur", dcc.Input(id="prominence",
                                                              type="number"),]), className="col-sm-2"),
                    html.Div(html.Label(["Largeur", dcc.Input(id="width",
                                                              type="number")]), className="col-sm-2"),
                ], className="row"),
                html.Div([
                    html.Div(html.P("Taille de la zone à enlever : "),
                         className="col-sm-4"),
                ], className="row"),
                html.Div([
                    html.Label(["Largeur cachée", dcc.Input(
                        id="removed_width", type="number")], className="col-sm-2"),
                    html.Div("", className="col-sm-7"),
                    html.Button(html.B("5.Filtrer les données"), className="contrast outline col-sm-3",
                                id="filter-selection-button", n_clicks=0)
                ], className="row"),
                html.Div(id='div-error-filter'),]
            )),
            html.Div(id="filter-data-div", children=html.Article(children=[
                html.H2("Courbe filtrée", className="col-sm-9"),
                dcc.Loading(dcc.Graph(id="test-filter-chart",
                                      figure={
                                          'layout':
                                          pio.templates["plotly_dark_custom"].layout
                                      }))]
            )),
            html.Div(id="div-table"),
            html.Article(
                children=[
                    html.Div(html.H2("Courbe de la VO2")),
                    html.Div(
                        children=dcc.Loading(dcc.Graph(
                            id="vo2-chart",
                            figure={
                                'layout':
                                pio.templates["plotly_dark_custom"].layout
                            }
                        )),
                        className="card"
                    )

                ],
                className="wrapper"
            ),
            dcc.Loading(html.Div(id="div-hr")),
        ],
            id="test-graphs-div"),

        html.Button(html.B("Imprimer en PDF"), className="contrast outline",
                    id="print-pdf", n_clicks=0),

        # dcc.Store stores the file data
        dcc.Loading(dcc.Store(id='data-upload', storage_type='session')),
        dcc.Store(id='seuils', storage_type='session'),
        dcc.Store(id='data-selection', storage_type='session'),
        dcc.Store(id='data-filtered', storage_type='session'),
        dcc.Store(id='peaks-parameters', storage_type='session'),
        dcc.Store(id='vo2-data', storage_type='session'),
        dcc.Store(id='analytics', storage_type='session')
    ])

get_store_callbacks(d)
get_figure_callbacks(d)
get_dropdown_callbacks(d)
get_threshold_callbacks(d)
get_div_callbacks(d)
get_p_callbacks(d)
get_button_callbacks(d)
get_modal_callbacks(d)
