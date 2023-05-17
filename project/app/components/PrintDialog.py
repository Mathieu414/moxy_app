from dash import html, dcc

PrintDialog = html.Dialog(
    [
        html.Div(
            html.Article(
                children=[
                    html.Header(
                        [
                            html.A(className="close", id="modal-print-abort"),
                            html.H1("Rapport PDF"),
                        ],
                        className="headings",
                    ),
                    html.Div(
                        children=[
                            dcc.Input(placeholder="Prénom", id="report-first-name"),
                            dcc.Input(placeholder="Nom", id="report-last-name"),
                        ],
                        id="modal-print-content",
                        className="center",
                    ),
                    html.Footer(
                        [
                            dcc.Loading(
                                html.Button(
                                    "Générer le rapport",
                                    id="modal-print-validate",
                                )
                            ),
                            html.Button(
                                "Télécharger le rapport",
                                id="btn-download-pdf",
                                className="hide",
                            ),
                            dcc.Download(id="download-pdf-file"),
                        ]
                    ),
                ],
                id="modal-print-article",
            ),
            id="spinner",
        ),
    ],
    id="modal-print",
    open=False,
)
