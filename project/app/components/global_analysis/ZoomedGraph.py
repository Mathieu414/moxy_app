from dash import html, dcc
from dash_iconify import DashIconify

ZoomedGraph = html.Div(
    id="zoom-chart-div",
    children=html.Article(
        children=[
            html.Div(
                [
                    html.H2(
                        "Courbe de la sélection",
                        className="center no-print",
                    )
                ]
            ),
            # Only when printing with the browser
            html.Div(
                [
                    html.H2(
                        "Courbe des groupes musculaires",
                        className="center print",
                    )
                ]
            ),
            # Only when printing with the browser
            html.Div(
                id="p-threshold",
                children=[
                    html.Div(
                        [
                            html.P("Seuil 1"),
                            dcc.Input(
                                id="threshold1-p",
                                type="number",
                                debounce=True,
                                disabled=True,
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.P("Seuil 2"),
                            dcc.Input(
                                id="threshold2-p",
                                type="number",
                                debounce=True,
                                disabled=True,
                            ),
                        ]
                    ),
                ],
                className="inline print",
            ),
            html.Div(
                id="inputs-threshold",
                children=[
                    html.Div(
                        [
                            html.P("Seuil 1 (bpm)"),
                            dcc.Input(
                                id="threshold1",
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
                                id="threshold2",
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
                dcc.Graph(
                    id="test-selected-chart",
                )
            ),
            html.Hr(),
            html.Div(
                children=[
                    html.Div(
                        [
                            html.Div(
                                html.P("Paramètres de detection des pauses:"),
                            ),
                            html.Label(
                                [
                                    "Hauteur (bpm)",
                                    dcc.Input(id="prominence", type="number"),
                                ],
                            ),
                            html.Label(
                                [
                                    "Largeur (s)",
                                    dcc.Input(id="width", type="number"),
                                ]
                            ),
                        ],
                        className="no-print",
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.P("Taille de la zone à enlever : "),
                            ),
                            html.Label(
                                [
                                    "Retirer à gauche (s)",
                                    dcc.Input(
                                        id="removed_width_left",
                                        type="number",
                                    ),
                                ]
                            ),
                            html.Label(
                                [
                                    "Retirer à droite (s)",
                                    dcc.Input(
                                        id="removed_width_right",
                                        type="number",
                                    ),
                                ],
                            ),
                            html.Button(
                                [
                                    DashIconify(icon="carbon:filter"),
                                    html.B("Filtrer les données"),
                                ],
                                id="filter-selection-button",
                                n_clicks=0,
                            ),
                        ],
                        className="no-print",
                    ),
                ],
                className="grid",
            ),
            html.Div(id="div-error-filter"),
        ]
    ),
)
