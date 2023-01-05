import base64
import io
from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
import numpy as np
import datetime
import plotly.express as px


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Moxy app"


app.layout = html.Div(
    children=[

        # header
        html.Div(
            children=[
                html.H1(
                    children="Analyse Moxy de test VO2",
                    className="header-title"),
                html.P(
                    children="Application pour analyser les données moxy d'un test VO2", className="header-description"
                ),
            ],
            className="header"
        ),

        # menu
        html.Div(
            children=[
                dcc.Upload(
                    id='upload-xlsx',
                    children=html.Button('Upload DataAverage.xlsx File'),

                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                dcc.Upload(
                    id='upload-txt',
                    children=html.Button('Upload Details.txt File'),

                    # Allow multiple files to be uploaded
                    multiple=True
                )
            ],
            className="menu",
        ),

        # graphs
        html.Div(
            children=[
                html.H2("Courbe de la session entière"),
                html.P(
                    "Sélectionnez un champ de données avec l'outil sélection en haut à droite"),
                html.Div(
                    children=dcc.Graph(
                        id="moxy-chart"
                    ),
                    className="card"
                )

            ],
            className="wrapper"
        ),
        # dcc.Store stores the file data
        dcc.Store(id='xlsx-data'),
        dcc.Store(id='txt-data'),
    ])


@app.callback(
    [Output('xlsx-data', 'data'),
     Output('txt-data', 'data')],
    [Input("upload-xlsx", "contents"),
     Input("upload-txt", "filename")],
    prevent_initial_call=True
)
def update_data(contents, filenames):
    data = []

    for content, filename in zip(contents, filenames):
        data.append(parse_data(content, filename))
    print(data)
    # return data.to_json()


def parse_data(content, filename):
    content_type, content_string = content.split(",")
    print(content_string)

    decoded = base64.b64decode(content_string)
    try:
        if "xlsx" in filename:
            # Assume that the user uploaded an excel file
            return pd.read_excel(io.BytesIO(decoded))
        elif "txt" or "tsv" in filename:
            # return the file in a raw form
            io.StringIO(decoded.decode("utf-8"))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])


if __name__ == '__main__':
    app.run_server(debug=True)
