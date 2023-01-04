import json
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import numpy as np
import datetime
import plotly.express as px


data = pd.read_csv("moxy_data.csv", header=2)

# get the current year
today = datetime.date.today()
year = today.year

# format the date
data["Date"] = pd.to_datetime(
    str(year) + "-" + data["mm-dd"] + "-" + data["hh:mm:ss"], format="%Y-%m-%d-%H:%M:%S")

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
                )
            ],
            className="header"
        ),

        # menu
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Session", className="menu-title"),
                        dcc.Dropdown(
                            id="session-filter",
                            options=[
                                {"label": session, "value": session}
                                for session in np.sort(data["Session Ct"].unique())
                            ],
                            value=data["Session Ct"][0],
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
                    "Sélectionnez un champ de données avec l'outil sélection en haut à gauche"),
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
                html.Div(
                    children=dcc.Graph(
                        id="zoom-chart"
                    ),
                    className="card"
                )

            ],
            className="wrapper"
        ),
        html.P(id='selected-data')
    ])


@app.callback(
    Output("moxy-chart", "figure"),
    Input("session-filter", "value")
)
def update_charts(session):
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
    Input("moxy-chart", "selectedData")
)
def display(selectedData):
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
    return fig2 if fig2 else None


if __name__ == '__main__':
    app.run_server(debug=True)
