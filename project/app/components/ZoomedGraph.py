from dash import html, dcc

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
            html.Div(
                [
                    html.H2(
                        "Courbe des groupes musculaires",
                        className="center print",
                    )
                ]
            ),
            html.Div(
                id="p-threshold",
                children=[
                    html.Div(
                        [
                            html.P("Seuil 1"),
                            dcc.Input(
                                id="seuil1-p",
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
                                id="seuil2-p",
                                type="number",
                                debounce=True,
                                disabled=True,
                            ),
                        ]
                    ),
                ],
                className="inline print",
            ),
            dcc.Loading(
                dcc.Graph(
                    id="test-zoom-chart",
                )
            ),
            html.Hr(),
            html.Div(
                [
                    html.Div(
                        html.P("Paramètres de detection des pauses:"),
                        className="col-sm-4",
                    ),
                ],
                className="row no-print",
            ),
            html.Div(
                [
                    html.Div(
                        html.Label(
                            [
                                "Hauteur (bpm)",
                                dcc.Input(id="prominence", type="number"),
                            ]
                        ),
                        className="col-sm-3",
                    ),
                    html.Div(
                        html.Label(
                            [
                                "Largeur (s)",
                                dcc.Input(id="width", type="number"),
                            ]
                        ),
                        className="col-sm-3",
                    ),
                ],
                className="row no-print",
            ),
            html.Div(
                [
                    html.Div(
                        html.P("Taille de la zone à enlever : "),
                        className="col-sm-4",
                    ),
                ],
                className="row no-print",
            ),
            html.Div(
                [
                    html.Label(
                        [
                            "Retirer à gauche (s)",
                            dcc.Input(
                                id="removed_width_left",
                                type="number",
                            ),
                        ],
                        className="col-sm-3",
                    ),
                    html.Label(
                        [
                            "Retirer à droite (s)",
                            dcc.Input(
                                id="removed_width_right",
                                type="number",
                            ),
                        ],
                        className="col-sm-3",
                    ),
                    html.Div("", className="col-sm-3"),
                    html.Button(
                        html.B("5.Filtrer les données"),
                        className="contrast outline col-sm-3",
                        id="filter-selection-button",
                        n_clicks=0,
                    ),
                ],
                className="row no-print",
            ),
            html.Div(id="div-error-filter"),
        ]
    ),
)
