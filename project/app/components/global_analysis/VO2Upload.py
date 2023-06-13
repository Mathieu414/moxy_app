from dash_extensions.enrich import html, dcc

VO2Upload = html.Article(
    children=[
        dcc.Upload(
            id="vo2-upload",
            children=html.Button(
                children="Importer les données VO2 du test",
                id="vo2_button",
                disabled=True,
                className="secondary outline",
            ),
            multiple=False,
            className="inputs",
            accept="application/xml,text/xml",
        ),
    ],
    className="menu no-print",
)
