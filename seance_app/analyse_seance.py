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
                html.H1(children="Moxy app", className="header-title"),
                html.P(
                    children="Analyse d'un fichier moxy", className="header-description"
                ),
            ],
            className="header"
        ),

        # menu
        html.Div(
            children=[
                dcc.Upload(
                    id='upload-data',
                    children=html.Button('Upload File'),
                ),
                html.Div(
                    children=[
                        html.Div(children="Session", className="menu-title"),
                        dcc.Dropdown(
                            id="session-filter",
                            # value=data["Session Ct"][0],
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
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
        html.Div(
            children=[
                html.H1("Visualisation de la sélection"),
                html.Div(
                    children=dcc.Graph(
                        id="zoom-chart"
                    ),
                    className="card"
                )

            ],
            className="wrapper"
        ),
        html.P(id='selected-data'),

        # dcc.Store stores the intermediate value
        dcc.Store(id='file-data'),
    ])


@app.callback(
    Output('file-data', 'data'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)
def update_data(uploadData):

    content_type, content_string = uploadData.split(",")
    decoded = base64.b64decode(content_string)

    data = pd.read_csv(io.StringIO(decoded.decode("utf-8")), header=2)

    # get the current year
    today = datetime.date.today()
    year = today.year

    # format the date
    data["Date"] = pd.to_datetime(
        str(year) + "-" + data["mm-dd"] + "-" + data["hh:mm:ss"], format="%Y-%m-%d-%H:%M:%S")

    return data.to_json()


@app.callback(
    Output('session-filter', 'options'),
    Output('session-filter', 'value'),
    Input('file-data', 'data'),
    prevent_initial_call=True)
def update_dropdown(data):
    data = pd.read_json(data)
    options = [{"label": session, "value": session}
               for session in np.sort(data["Session Ct"].unique())]
    return options, data["Session Ct"][0]


@app.callback(
    Output("moxy-chart", "figure"),
    Input("session-filter", "value"),
    State('file-data', 'data'),
    prevent_initial_call=True)
def update_charts(session, data):
    data = pd.read_json(data)
    mask = (
        (data["Session Ct"] == session)
    )
    filtered_data = data.loc[mask, :]

    fig = px.scatter(filtered_data, x='Date', y='SmO2 Live')
    fig.update_traces(mode='lines+markers',
                      hovertemplate="%{y:.2f}%<extra></extra>", marker_size=10)
    fig.update_xaxes(showgrid=False)

    fig.update_yaxes(type='linear')

    fig.update_layout(clickmode='event+select')
    return fig


@ app.callback(
    Output("zoom-chart", "figure"),
    Input("moxy-chart", "selectedData"),
    State('file-data', 'data'),
    prevent_initial_call=True)
def display(selectedData, data):
    data = pd.read_json(data)
    selected_dates = []
    if selectedData and selectedData['points']:
        for point in selectedData["points"]:
            selected_dates.append(point['x'])
        filtered_df = data.query("Date == @selected_dates")
        fig2 = px.scatter(filtered_df, x='Date', y='SmO2 Live')
        fig2.update_traces(mode='lines+markers',
                           hovertemplate="%{y:.2f}%<extra></extra>", marker_size=10)
        fig2.update_xaxes(showgrid=False)

        fig2.update_yaxes(type='linear')

        fig2.update_layout(clickmode='event+select')
        return fig2


if __name__ == '__main__':
    app.run_server(debug=True)
