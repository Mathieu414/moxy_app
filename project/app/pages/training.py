import base64
import io
import dash_labs as dl
from dash_extensions.enrich import (
    Output,
    Input,
    State,
    Trigger,
    callback,
    html,
    dcc,
    DashBlueprint,
    ServersideOutput,
)

from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

from scipy import signal

pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"]["layout"]["paper_bgcolor"] = "#181c25"
pio.templates["plotly_dark_custom"]["layout"]["plot_bgcolor"] = "#181c25"
pio.templates["plotly_dark_custom"]["layout"]["dragmode"] = "select"


def seance_page():
    seance_page = DashBlueprint()

    seance_page.layout = html.Div(
        children=[
            # header
            html.Header(
                children=[
                    html.H1(children="Séance", className="center"),
                    html.P(
                        children="Analyse d'une séance à partir d'un fichier .csv",
                        className="center",
                    ),
                ],
                className="container",
            ),
            # menu
            html.Article(
                children=[
                    dcc.Upload(
                        id="training-upload",
                        children=html.Button(
                            html.B("Charger le fichier"), role="button"
                        ),
                    ),
                    html.P(children="Session", className="menu-title"),
                    dcc.Dropdown(
                        id="session-filter",
                    ),
                ],
                className="menu",
            ),
            # graphs
            html.Div(
                children=[
                    html.H2("Courbe de la session entière"),
                    html.P(
                        "Sélectionnez un champ de données avec l'outil sélection en haut à droite"
                    ),
                    html.Div(
                        children=dcc.Graph(id="moxy-chart", figure=go.Figure()),
                        className="card",
                    ),
                ],
                className="wrapper",
            ),
            html.Div(
                children=[
                    html.Article(
                        children=[
                            html.H1("Visualisation de la sélection"),
                            dcc.Graph(id="zoom-chart", figure=go.Figure()),
                        ]
                    )
                ],
                className="wrapper",
            ),
            # dcc.Store stores the intermediate value
            dcc.Store(id="file-data", storage_type="session"),
        ]
    )

    @callback(
        ServersideOutput("file-data", "data"),
        Input("training-upload", "contents"),
        prevent_initial_call=True,
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
            str(year) + "-" + data["mm-dd"] + "-" + data["hh:mm:ss"],
            format="%Y-%m-%d-%H:%M:%S",
        )

        return data

    @callback(
        Output("session-filter", "options"),
        Output("session-filter", "value"),
        Input("file-data", "data"),
    )
    def update_dropdown(data):
        if data:
            options = [
                {"label": session, "value": session}
                for session in np.sort(data["Session Ct"].unique())
            ]
            return options, data["Session Ct"][0]
        else:
            raise PreventUpdate

    @callback(
        Output("moxy-chart", "figure"),
        Input("session-filter", "value"),
        State("file-data", "data"),
    )
    def update_charts(session, data):
        mask = data["Session Ct"] == session
        filtered_data = data.loc[mask, :]

        fig = px.scatter(filtered_data, x="Date", y="SmO2 Live")
        fig.update_traces(
            mode="lines+markers",
            hovertemplate="%{y:.2f}%<extra></extra>",
            marker_size=1,
        )
        fig.update_xaxes(showgrid=False)

        fig.update_yaxes(type="linear")

        fig.update_layout(clickmode="event+select")
        return fig

    @callback(
        Output("zoom-chart", "figure"),
        Input("moxy-chart", "selectedData"),
        State("file-data", "data"),
        prevent_initial_call=True,
    )
    def display(selectedData, data):
        selected_dates = []
        if selectedData and selectedData["points"]:
            for point in selectedData["points"]:
                selected_dates.append(point["x"])
            filtered_df = data.query("Date == @selected_dates")
            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=filtered_df["Date"],
                    y=signal.savgol_filter(
                        filtered_df["SmO2 Live"],
                        50,  # window size used for filtering
                        3,
                    ),
                )
            ),  # order of fitted polynomial)
            fig2.update_traces(
                mode="lines+markers",
                hovertemplate="%{y:.2f}%<extra></extra>",
                marker_size=1,
            )
            fig2.update_xaxes(showgrid=False)

            fig2.update_yaxes(type="linear")

            fig2.update_layout(clickmode="event+select")
            return fig2
        else:
            raise PreventUpdate

    return seance_page
