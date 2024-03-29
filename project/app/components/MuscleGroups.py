from dash import html, dcc

# muscle groups modal
MuscleGroups = html.Article(
    children=[
        html.Button(
            children=html.B("Définir les groupes musculaires"),
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
                                html.B(
                                    "Vérifier les groupes musculaires correspondant aux numéros de Moxy sur le fichier Details.txt"
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
