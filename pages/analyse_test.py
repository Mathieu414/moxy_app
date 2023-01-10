import base64
import io
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import pandas as pd
import numpy as np
import plotly.express as px
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

dash.register_page(__name__)

pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"]['layout']['paper_bgcolor'] = '#141e26'
pio.templates["plotly_dark_custom"]['layout']['plot_bgcolor'] = '#141e26'
pio.templates.default = "plotly_dark_custom"


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
        html.Article(children=[
            html.P(
                'Charger les fichiers DataAverage.xlsx et Details.txt'),
            dcc.Upload(
                id='upload',
                children=html.Button(
                    'Upload'),
                # Allow multiple files to be uploaded
                multiple=True
            ),
        ],
            className="menu",
        ),

        # graphs
        html.Article(
            children=[
                html.H2("Courbe des groupes musculaires"),
                html.Div(id="inputs-threshold", className='grid'),
                html.Div(
                    children=dcc.Graph(
                        id="test-chart",
                        figure={
                            'layout':
                            pio.templates["plotly_dark_custom"].layout
                        }
                    ),
                    className="card"
                )

            ],
            className="wrapper"
        ),
        # dcc.Store stores the file data
        dcc.Store(id='data_upload', storage_type='session'),
        html.Div(id="div-hr"),
    ])


@callback(
    Output('data_upload', 'data'),
    [Input("upload", "contents"), Input("upload", "filename")],
    prevent_initial_call=True
)
def update(contents, filenames):
    if 'Details.txt' in filenames:
        t_id = filenames.index('Details.txt')
        x_id = filenames.index('DataAverage.xlsx')
        data = []
        for content, filename in zip(contents, filenames):
            data.append(parse_data(content, filename))

        smo_cols = [col for col in data[x_id].columns if 'SmO2' in col]

        col_names = dict(zip(smo_cols, data[t_id]))

        data[x_id].rename(columns=col_names, inplace=True)

        # check if the elements are in the right order
        if t_id == 0:
            data[0], data[1] = data[1], data[0]
        data[0].replace(0, np.nan, inplace=True)
        data[0] = data[0].to_json()
        return [data[0], data[1]]


@callback(
    Output('test-chart', 'figure'),
    [Input('data_upload', 'data'),
     Input('seuil1', 'value'),
     Input('seuil2', 'value')]
)
def update_graph(data, seuil1, seuil2):
    data[0] = pd.read_json(data[0])
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for n in data[1]:
        fig.add_trace(go.Scatter(
            x=data[0]["Time[s]"], y=data[0][n], name=n,  hovertemplate="%{y:.2f} %<extra></extra>"), secondary_y=False)

    if "HR[bpm]" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["HR[bpm]"],
                                 name="HR", hovertemplate="%{y:.2f} bpm<extra></extra>"), secondary_y=True)

    fig.update_traces(mode='lines+markers', marker_size=1)
    fig.update_xaxes(showgrid=False, title="Temps")

    fig.update_yaxes(title_text="Desoxygenation", secondary_y=False)
    if "HR[bpm]" in data[0].columns:
        fig.update_yaxes(title_text="Heart Rate", secondary_y=True)
        if seuil1:
            fig.add_hline(y=seuil1, line_width=3, line_dash="dash",
                          line_color="green", secondary_y=True)
        if seuil2:
            fig.add_hline(y=seuil2, line_width=3, line_dash="dash",
                          line_color="yellow", secondary_y=True)

    fig.update_layout(
        clickmode='event+select',
        height=500,
        margin=dict(l=20, r=20, t=30, b=20))
    return fig


def parse_data(content, filename):
    content_type, content_string = content.split(",")
    decoded = base64.b64decode(content_string)
    try:
        if "xlsx" in filename:
            # Assume that the user uploaded an excel file
            return pd.read_excel(io.BytesIO(decoded))

        elif "Details.txt" in filename:
            file = decoded.decode('utf-8')
            m = re.findall("\) - ([\w\s+]+)\n", file)
            return m

    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])


@callback(
    Output('div-hr', 'children'),
    Input('data_upload', 'data')
)
def add_graph(data):
    data[0] = pd.read_json(data[0])
    if "HR[bpm]" in data[0].columns:
        children = [html.H2("Desoxygénation musculaire en fonction du HR")]
        for n in data[1]:
            fig = px.scatter(x=data[0]["HR[bpm]"],
                             y=data[0][n], marginal_y="violin",
                             labels=dict(x="HR", y="Desoxygenation " + n))

            children.extend([html.H4(n),
                             html.Div(
                children=dcc.Graph(
                            id="hr-" + n,
                            figure=fig
                            ),
                className="card"
            )]

            )
        content = html.Article(children=children,
                               className="wrapper"
                               )
        return content


@callback(
    Output('inputs-threshold', 'children'),
    Input('data_upload', 'data')
)
def add_thresholds(data):
    data[0] = pd.read_json(data[0])
    if "HR[bpm]" in data[0].columns:
        children = [
            html.Div([
                html.P("Seuil 1"),
                dcc.Input(id="seuil1", type='number')
            ]),
            html.Div([
                html.P("Seuil 2"),
                dcc.Input(id="seuil2", type='number')
            ])]
        return children
