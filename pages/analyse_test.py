import base64
import io
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

dash.register_page(__name__)

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
            className="center"
        ),

        # menu
        html.Article(
            children=[
                dcc.Upload(
                    id='upload-xlsx',
                    children=html.Button('Upload DataAverage.xlsx File'),

                ),
                dcc.Upload(
                    id='upload-txt',
                    children=html.Button('Upload Details.txt File'),
                )
            ],
            className="menu",
        ),

        # graphs
        html.Div(
            children=[
                html.H2("Courbe des groupes musculaires"),
                html.Div(
                    children=dcc.Graph(
                        id="test-chart"
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


@callback(
    Output('xlsx-data', 'data'),
    [Input("upload-xlsx", "contents"), Input("upload-xlsx", "filename")],
    prevent_initial_call=True
)
def update_xlsx(content, filename):
    data = parse_data(content, filename)
    print(type(data))
    return data.to_json()


@callback(
    Output('txt-data', 'data'),
    [Input("upload-txt", "contents"), Input("upload-txt", "filename")],
    prevent_initial_call=True
)
def update_txt(content, filename):
    data = parse_data(content, filename)
    print("les données" + data)
    # return data.to_json()


@callback(
    Output('test-chart', 'figure'),
    Input('xlsx-data', 'data'),
    prevent_initial_call=True
)
def update_graph(data):
    data = pd.read_json(data)
    print(data)

    fig = px.scatter(data, x="Time[s]", y="SmO2 -  3[%]")
    fig.add_scatter(x=data["Time[s]"], y=data["SmO2 -  4[%]"])

    fig.update_traces(mode='lines+markers',
                      hovertemplate="%{y:.2f}%<extra></extra>", marker_size=1)
    fig.update_xaxes(showgrid=False)

    fig.update_yaxes(type='linear')

    fig.update_layout(clickmode='event+select')
    return fig


def parse_data(content, filename):
    content_type, content_string = content.split(",")

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
