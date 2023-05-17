from dash import html, dcc

# muscle groups modal
MuscleGroups = html.Article(
    children=[
        html.P(html.B("2.Définir les groupes musculaires")),
        html.Button(
            children="Définir",
            id="modal_open",
            disabled=True,
            className="secondary outline",
        ),
        html.Dialog(
            [
                html.Article(
                    [
                        html.Div(
                            [
                                html.A(className="close", id="modal_abort"),
                                html.H2("Définir les groupes musulaires"),
                                html.H3(
                                    "Vérifier les groupes musculaires correspondant aux numéro de Moxy sur le fichier Details.txt"
                                ),
                            ],
                            className="headings",
                        ),
                        html.Div(id="modal_content", className="center"),
                        html.Footer(html.Button("Confirmer", id="modal_close")),
                    ]
                )
            ],
            id="modal",
            open=False,
        ),
    ],
    className="menu no-print",
)
