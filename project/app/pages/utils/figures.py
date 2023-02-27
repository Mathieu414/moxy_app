import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.api as sm


def create_figure(data):
    """
    Create figure with the different muscles group and the HR

    Args:
        data (list): [0] contains a Dataframe with the data to plot, [1] contains the muscle groups

    Returns:
        go.Figure : figure to be plotted
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for n in data[1]:
        fig.add_trace(go.Scattergl(
            x=data[0]["Time[s]"], y=data[0][n], name=n,  hovertemplate="%{y:.2f} %<extra></extra>", mode='lines+markers'), secondary_y=False)

    if "HR[bpm]" in data[0].columns:
        fig.add_trace(go.Scattergl(x=data[0]["Time[s]"], y=data[0]["HR[bpm]"],
                                   name="HR", hovertemplate="%{y:.2f} bpm<extra></extra>", mode='lines+markers'), secondary_y=True)

    if "Seuil 1" in data[0].columns:
        fig.add_trace(go.Scattergl(x=data[0]["Time[s]"], y=data[0]["Seuil 1"], line_width=3, line_dash="dash",
                                   line_color="green", name="Seuil 1"), secondary_y=True)

    if "Seuil 2" in data[0].columns:
        fig.add_trace(go.Scattergl(x=data[0]["Time[s]"], y=data[0]["Seuil 2"], line_width=3, line_dash="dash",
                                   line_color="yellow", name="Seuil 2"), secondary_y=True)

    if "VO2" in data[0].columns:
        fig.add_trace(go.Scattergl(
            x=data[0]["Time[s]"], y=(data[0]["VO2"]*10), name="VO2"), secondary_y=True)

    if "FC" in data[0].columns:
        fig.add_trace(go.Scattergl(
            x=data[0]["Time[s]"], y=(data[0]["FC"]), name="FC"), secondary_y=True)

    fig.update_traces(marker_size=1)
    fig.update_xaxes(showgrid=False, title="Temps")
    fig.update_yaxes(title_text="Desoxygenation", secondary_y=False)
    fig.update_layout(
        clickmode='event+select',
        height=500,
        margin=dict(l=20, r=20, t=30, b=20))

    return fig


def create_filtered_figure(data):
    """
    Same as create_figure, but the data is a list of dataframes of same columns, that has to be concatenated into one big df.
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    data[0] = pd.concat(data[0])

    for n in data[1][0]:
        fig.add_trace(go.Scattergl(
            x=data[0]["Time[s]"], y=data[0][n], name=n,  hovertemplate="%{y:.2f} %<extra></extra>", mode='lines+markers'), secondary_y=False)

    if "HR[bpm]" in data[0].columns:
        fig.add_trace(go.Scattergl(x=data[0]["Time[s]"], y=data[0]["HR[bpm]"],
                                   name="HR", hovertemplate="%{y:.2f} bpm<extra></extra>", mode='lines+markers'), secondary_y=True)

    if "Seuil 1" in data[0].columns:
        fig.add_trace(go.Scattergl(x=data[0]["Time[s]"], y=data[0]["Seuil 1"], line_width=3, line_dash="dash",
                                   line_color="green", name="Seuil 1"), secondary_y=True)

    if "Seuil 2" in data[0].columns:
        fig.add_trace(go.Scattergl(x=data[0]["Time[s]"], y=data[0]["Seuil 2"], line_width=3, line_dash="dash",
                                   line_color="yellow", name="Seuil 2"), secondary_y=True)

    fig.update_traces(marker_size=1)
    fig.update_xaxes(showgrid=False, title="Temps")
    fig.update_yaxes(title_text="Desoxygenation", secondary_y=False)
    fig.update_layout(
        clickmode='event+select',
        height=500,
        margin=dict(l=20, r=20, t=30, b=20))

    return fig


def create_vo2_figure(data):

    fig = go.Figure()

    data[0] = pd.concat(data[0])

    if "VO2" in data[0].columns:
        print("VO2")
        # fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["VO2"],name="VO2"))
        for n in data[1][0]:
            print(n)
            trendline = sm.nonparametric.lowess(data[0][n],
                                                data[0]["VO2"],
                                                frac=0.5)
            fig.add_trace(go.Scattergl(
                x=data[0]["VO2"], y=data[0][n], name=n,  hovertemplate="%{y:.2f} %<extra></extra>", mode='markers'))
            fig.add_trace(go.Scatter(x=trendline[:, 0],
                                     y=trendline[:, 1],
                                     mode='lines',
                                     name="Tendance",
                                     line_shape='spline'))

    return fig
