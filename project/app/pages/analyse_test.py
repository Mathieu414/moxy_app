import base64
import io
import dash
from dash import Dash, html, dcc, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import plotly.express as px
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from scipy import signal
import statsmodels.api as sm

dash.register_page(__name__)

pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"]['layout']['paper_bgcolor'] = '#141e26'
pio.templates["plotly_dark_custom"]['layout']['plot_bgcolor'] = '#141e26'
pio.templates.default = "plotly_dark_custom"

debug = True

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
                id='test-upload',
                children=html.Button(
                    'Upload'),
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Button("Effacer les données ",
                        className="contrast outline", id="clear-button", n_clicks=0)
        ],
            className="menu",
        ),

        # graphs
        html.Article(
            children=[
                html.Div(children=[
                    html.Div(html.H2("Courbe des groupes musculaires"),
                             className="col-8"),
                    html.Div(dcc.Dropdown(
                        id="test-choice"), className="col")
                ], className="row"),
                html.P(html.B("Selectionnez la zone du test")),
                html.Div(id="inputs-threshold",
                         children=[
                             html.Div([
                                 html.P("Seuil 1"),
                                 dcc.Input(
                                     id="seuil1", type='number', debounce=True, disabled=True)
                             ]),
                             html.Div([
                                 html.P("Seuil 2"),
                                 dcc.Input(
                                     id="seuil2", type='number', debounce=True, disabled=True)
                             ])],
                         className='grid'),
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
        html.Div(id="zoom-chart-div"),
        # dcc.Store stores the file data
        dcc.Store(id='data-upload', storage_type='session'),
        html.Div(id="div-hr"),
        dcc.Store(id='data-selection', storage_type='session'),
    ])


@callback(
    Output('data-upload', 'data'),
    [Input("test-upload", "contents"),
     Input("test-upload", "filename"),
     Input("seuil1", 'value'),
     Input("seuil2", 'value'),
     Input("clear-button", "n_clicks")],
    [State("data-upload", 'data'),
     State("test-choice", 'value')],
    prevent_initial_call=True,
)
def data_upload(contents, filenames, seuil1, seuil2, n_clicks, stored_data, value):
    if debug:
        print("--data-upload--")
    if (ctx.triggered_id == "test-upload") and ('Details.txt' in filenames):
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
        if stored_data:
            stored_data.append([data[0], data[1]])
            return stored_data
        else:
            return [[data[0], data[1]]]
    if debug:
        print("valeur de seuil1")
        print(seuil1)
        print("valeur de seuil2")
        print(seuil2)
    if (ctx.triggered_id in ["seuil1", "seuil2"]) and (not all(s is None for s in (seuil1, seuil2))):
        if debug:
            print("Seuil 1 or Seuil 2 are trigered and are not None")
        df = pd.read_json(stored_data[value][0])
        if seuil1 is not None:
            df["Seuil 1"] = seuil1
        if seuil2 is not None:
            df["Seuil 2"] = seuil2
        df = df.to_json()
        stored_data[value][0] = df
        return stored_data
    if (ctx.triggered_id == "clear-button") and (n_clicks > 0):
        if debug:
            print("Clearing data")
        stored_data = None
        return stored_data
    else:
        if debug:
            print("prevent update data_upload")
        raise PreventUpdate


@ callback(
    Output('test-choice', 'options'),
    Input('data-upload', 'data'),
    State('test-choice', 'options')
)
def dropdown_update(data, options):
    if debug:
        print("--dropdown_update--")
    if data:
        if debug:
            print("longueur de la liste 'data' : " + str(len(data)))
        new_options = [{"label": "Test n°" + str(session+1), "value": session}
                       for session in range(len(data))]
        if (options is not None):
            if len(options) != len(new_options):
                return new_options
        if options is None:
            return new_options
        else:
            raise PreventUpdate
    if (data is None) and (options is not None):
        if debug:
            print("Data is None but options is not None")
        return {}
    else:
        raise PreventUpdate


@ callback(
    [Output('seuil1', 'disabled'),
     Output('seuil2', 'disabled'),
     Output('seuil1', 'value'),
     Output('seuil2', 'value')],
    Input('test-choice', 'value'),
    State('data-upload', 'data'),
    prevent_initial_call=True
)
def check_thresholds(value, data):
    if debug:
        print("--check_thresholds--")
    if (data is not None) and (value is not None):
        if debug:
            print("dataset columns: ")
            print(pd.read_json(data[value][0]).columns)
            print("Test de 'value' :")
            print(value == False)
        data = data[value]
        data[0] = pd.read_json(data[0])
        if "HR[bpm]" in data[0].columns:
            if debug:
                print("threshold enabled")
            value_seuil1 = None
            value_seuil2 = None
            if ("Seuil 1" in data[0].columns):
                value_seuil1 = data[0]["Seuil 1"][0]
                print(value_seuil1)
            if ("Seuil 2" in data[0].columns):
                value_seuil2 = data[0]["Seuil 2"][0]
                print(value_seuil2)
            return [False, False, value_seuil1, value_seuil2]
        else:
            if debug:
                print("HR is not in data")
            return [True, True, None, None]
    else:
        if debug:
            print("data or value is None")
        return [True, True, None, None]


@ callback(
    Output('test-chart', 'figure'),
    Input('test-choice', 'value'),
    State('data-upload', 'data'),
    prevent_initial_call=True
)
def update_graph(value, data):
    if debug:
        print("--update_graph--")
        print(value)
        print((data is None))
    if (value is not None) and (data is not None):
        print("value is not None")
        data = data[value]
        data[0] = pd.read_json(data[0])
        fig = create_figure(data)
        print("create figure :")
        return fig
    if (value == 0) and (data is None):
        print("value is None")
        return {'layout': pio.templates["plotly_dark_custom"].layout}
    else:
        raise PreventUpdate


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


def create_figure(data):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for n in data[1]:
        fig.add_trace(go.Scatter(
            x=data[0]["Time[s]"], y=signal.savgol_filter(data[0][n], 40, 3), name=n,  hovertemplate="%{y:.2f} %<extra></extra>", mode='lines+markers'), secondary_y=False)

    if "HR[bpm]" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=signal.savgol_filter(data[0]["HR[bpm]"], 40, 4),
                                 name="HR", hovertemplate="%{y:.2f} bpm<extra></extra>", mode='lines+markers'), secondary_y=True)

    if "Seuil 1" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["Seuil 1"], line_width=3, line_dash="dash",
                                 line_color="green", name="Seuil 1"), secondary_y=True)

    if "Seuil 2" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["Seuil 2"], line_width=3, line_dash="dash",
                                 line_color="yellow", name="Seuil 2"), secondary_y=True)

    fig.update_traces(marker_size=1)
    fig.update_xaxes(showgrid=False, title="Temps")
    fig.update_yaxes(title_text="Desoxygenation", secondary_y=False)
    fig.update_layout(
        clickmode='event+select',
        height=500,
        margin=dict(l=20, r=20, t=30, b=20))

    return fig


@ callback(
    Output("data-selection", "data"),
    [Input("test-chart", "selectedData"),
     Input('test-choice', 'value')],
    State('data-upload', 'data'),
    prevent_initial_call=True)
def store_filtered_data(selectedData, value, data):
    if debug:
        print("--store_filtered_data--")
    if ctx.triggered_id == "test-chart":
        if debug:
            print("Creating data selection chart")
        data = data[value]
        data[0] = pd.read_json(data[0])
        selected_time = []
        if selectedData and selectedData['points']:
            for point in selectedData["points"]:
                selected_time.append(point['x'])
            data[0] = data[0].query("`Time[s]` == @selected_time")
            data[0] = data[0].to_json()
            return data
    if ctx.triggered_id == "test-choice":
        if debug:
            print("erasing data-selection")
        return {}
    else:
        raise PreventUpdate


@ callback(
    Output('zoom-chart-div', 'children'),
    Input('data-selection', 'data'),
)
def display_filtered_data(data):
    fig = {'layout': pio.templates["plotly_dark_custom"].layout}
    if data:
        if debug:
            print("create figure")
        data[0] = pd.read_json(data[0])
        fig = create_figure(data)
    content = html.Article(children=[
        html.H2("Courbe de la sélection"),
        dcc.Graph(figure=fig)],
        className="wrapper"
    )
    return content


@ callback(
    Output('div-hr', 'children'),
    Input('data-selection', 'data')
)
def add_graph(data):
    if data:
        data[0] = pd.read_json(data[0])
        if "HR[bpm]" in data[0].columns:
            children = [html.H2("Desoxygénation musculaire en fonction du HR")]
            for n in data[1]:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data[0]["HR[bpm]"],
                                         y=data[0][n],
                                         mode='markers',
                                         showlegend=False))

                fig.add_trace(go.Histogram2dContour(x=data[0]["HR[bpm]"],
                                                    y=data[0][n],
                                                    colorscale=[
                                                        [0, '#141e26'], [1, '#636efa ']],
                                                    showscale=False,
                                                    contours_showlines=False))
                trendline = sm.nonparametric.lowess(data[0][n],
                                                    data[0]["HR[bpm]"],
                                                    frac=0.5,
                                                    missing="drop")
                fig.add_trace(go.Scatter(x=trendline[:, 0],
                                         y=trendline[:, 1],
                                         mode='lines',
                                         line_color='#ab63fa',
                                         name="Tendance",
                                         line_shape='spline'))
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
    else:
        return {}
