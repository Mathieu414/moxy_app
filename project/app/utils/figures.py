import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.functions as fc
import plotly.io as pio


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
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=data[0][n],
                name=n,
                hovertemplate="%{y:.2f} %<extra></extra>",
                mode="lines+markers",
            ),
            secondary_y=False,
        )

    if "HR[bpm]" in data[0].columns:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=data[0]["HR[bpm]"],
                name="HR",
                hovertemplate="%{y:.2f} bpm<extra></extra>",
                mode="lines+markers",
            ),
            secondary_y=True,
        )

    if "Seuil 1" in data[0].columns:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=data[0]["Seuil 1"],
                line_width=3,
                line_dash="dash",
                line_color="green",
                name="Seuil 1",
            ),
            secondary_y=True,
        )

    if "Seuil 2" in data[0].columns:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=data[0]["Seuil 2"],
                line_width=3,
                line_dash="dash",
                line_color="yellow",
                name="Seuil 2",
            ),
            secondary_y=True,
        )

    if "VO2" in data[0].columns:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=(data[0]["VO2"] * 10),
                name="VO2",
                mode="lines",
                connectgaps=True,
            ),
            secondary_y=True,
        )

    if "FC" in data[0].columns:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=(data[0]["FC"]),
                name="FC",
                mode="lines+markers",
                connectgaps=True,
            ),
            secondary_y=True,
        )

    fig.update_traces(marker_size=1)
    fig.update_xaxes(showgrid=False, title="Temps (s)")
    fig.update_yaxes(title_text="Desoxygenation (%)", secondary_y=False)
    fig.update_layout(
        xaxis=dict(showgrid=True, gridwidth=3),
        yaxis=dict(showgrid=True, gridwidth=3),
        clickmode="event+select",
        height=500,
        margin=dict(l=20, r=20, t=30, b=20),
    )

    return fig


def create_filtered_figure(data):
    """
    Same as create_figure, but the data is a list of dataframes of same columns, that has to be concatenated into one big df.
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    data[0] = pd.concat(data[0])

    for n in data[1][0]:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=data[0][n],
                name=n,
                hovertemplate="%{y:.2f} %<extra></extra>",
                mode="lines+markers",
            ),
            secondary_y=False,
        )

    if "HR[bpm]" in data[0].columns:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=data[0]["HR[bpm]"],
                name="HR",
                hovertemplate="%{y:.2f} bpm<extra></extra>",
                mode="lines+markers",
            ),
            secondary_y=True,
        )

    if "Seuil 1" in data[0].columns:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=data[0]["Seuil 1"],
                line_width=3,
                line_dash="dash",
                line_color="green",
                name="Seuil 1",
            ),
            secondary_y=True,
        )

    if "Seuil 2" in data[0].columns:
        fig.add_trace(
            go.Scattergl(
                x=data[0]["Time[s]"],
                y=data[0]["Seuil 2"],
                line_width=3,
                line_dash="dash",
                line_color="yellow",
                name="Seuil 2",
            ),
            secondary_y=True,
        )

    fig.update_traces(marker_size=1)
    fig.update_xaxes(showgrid=False, title="Temps (s)")
    fig.update_yaxes(title_text="Desoxygenation (%)", secondary_y=False)
    fig.update_layout(
        xaxis=dict(showgrid=True, gridwidth=3),
        yaxis=dict(showgrid=True, gridwidth=3),
        clickmode="event+select",
        height=500,
        margin=dict(l=20, r=20, t=30, b=20),
    )

    return fig


def create_vo2_figure(data):
    fig = go.Figure()

    data[0] = pd.concat(data[0])

    colors = pio.templates["plotly_dark_custom"]["layout"]["colorway"]

    if "VO2" in data[0].columns:
        print("VO2")
        # fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["VO2"],name="VO2"))
        for i, n in enumerate(data[1][0]):
            px, py = fc.segments_fit(data[0]["VO2"], data[0][n], 4)
            fig.add_trace(
                go.Scattergl(
                    x=data[0]["VO2"],
                    y=data[0][n],
                    name=n,
                    hovertemplate="%{y:.2f} %<extra></extra>",
                    mode="markers",
                    marker=dict(color=colors[i]),
                )
            )
            fig.add_trace(
                go.Scattergl(
                    x=px,
                    y=py,
                    mode="lines",
                    name="Tendance",
                    line=dict(color=colors[i]),
                )
            )
        fig.update_layout(
            xaxis=dict(showgrid=True, gridwidth=3),
            yaxis=dict(showgrid=True, gridwidth=3),
            xaxis_title="VO2 (mL/min)",
            yaxis_title="Desoxygénation (%)",
            height=500,
            margin=dict(l=20, r=20, t=30, b=20),
        )

    return fig
