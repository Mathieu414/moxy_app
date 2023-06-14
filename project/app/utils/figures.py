import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.functions as fc
import plotly.io as pio
from sklearn.linear_model import LinearRegression
import numpy as np


def create_figure(data, muscle_groups, value, thresholds, linear_reg=False):
    """
    Create figure with the different muscles group and the HR

    Args:
        data (pd.Dataframe): Dataframe with the data to plot,
        muscle_groups (dict values): muscle column values of the dataframe

    Returns:
        go.Figure : figure to be plotted
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    data = checks(data, muscle_groups, thresholds)

    colors = pio.templates["plotly_dark_custom"]["layout"]["colorway"]

    for i, n in enumerate(list(muscle_groups.values())):
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data[n],
                name=n,
                hovertemplate="%{y:.2f} %<extra></extra>",
                mode="lines+markers",
                line=dict(color=colors[i]),
            ),
            secondary_y=False,
        )
        if linear_reg:
            x_pred = np.array(data["Time[s]"]).reshape((-1, 1))
            model = LinearRegression().fit(x_pred, y=data[n])
            y_pred = model.predict(x_pred)
            fig.add_trace(
                go.Scattergl(
                    x=data["Time[s]"],
                    y=y_pred,
                    name="Tendance de " + n,
                    mode="lines",
                    line=dict(color=colors[i]),
                )
            )

    if "HR[bpm]" in data.columns:
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data["HR[bpm]"],
                name="HR",
                hovertemplate="%{y:.2f} bpm<extra></extra>",
                mode="lines+markers",
            ),
            secondary_y=True,
        )

    if "Seuil 1" in data.columns:
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data["Seuil 1"],
                line_width=3,
                line_dash="dash",
                line_color="green",
                name="Seuil 1",
            ),
            secondary_y=True,
        )

    if "Seuil 2" in data.columns:
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data["Seuil 2"],
                line_width=3,
                line_dash="dash",
                line_color="yellow",
                name="Seuil 2",
            ),
            secondary_y=True,
        )

    if "VO2" in data.columns:
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=(data["VO2"] * 10),
                name="VO2",
                mode="lines",
                connectgaps=True,
            ),
            secondary_y=True,
        )

    if "FC" in data.columns:
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=(data["FC"]),
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


def create_filtered_figure(data, muscle_groups, value, thresholds):
    """
    Same as create_figure, but the data is a list of dataframes of same columns, that has to be concatenated into one big df.
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    data = pd.concat(data)

    data = checks(data, muscle_groups, thresholds)

    for n in muscle_groups.values():
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data[n],
                name=n,
                hovertemplate="%{y:.2f} %<extra></extra>",
                mode="lines+markers",
            ),
            secondary_y=False,
        )

    if "HR[bpm]" in data.columns:
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data["HR[bpm]"],
                name="HR",
                hovertemplate="%{y:.2f} bpm<extra></extra>",
                mode="lines+markers",
            ),
            secondary_y=True,
        )

    if "Seuil 1" in data.columns:
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data["Seuil 1"],
                line_width=3,
                line_dash="dash",
                line_color="green",
                name="Seuil 1",
            ),
            secondary_y=True,
        )

    if "Seuil 2" in data.columns:
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data["Seuil 2"],
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


def create_vo2_figure(data, muscle_groups):
    fig = go.Figure()

    data = pd.concat(data)

    colors = pio.templates["plotly_dark_custom"]["layout"]["colorway"]

    if "VO2" in data.columns:
        print("VO2")
        for i, n in enumerate(list(muscle_groups.keys())):
            px, py = fc.segments_fit(data["VO2"], data[n], 4)
            fig.add_trace(
                go.Scattergl(
                    x=data["VO2"],
                    y=data[n],
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


def create_trend_figure(data, muscle_groups):
    """
    Create figure with the different muscles group and the HR

    Args:
        data (pd.Dataframe): Dataframe with the data to plot,
        muscle_groups (dict values): muscle column values of the dataframe

    Returns:
        go.Figure : figure to be plotted
        dictionary : {muscle_group : tuple ( in [0] : model intercept
                                             in [1] : model coef)}
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    print(data)

    data = checks(data, muscle_groups, None)

    print(data)

    colors = pio.templates["plotly_dark_custom"]["layout"]["colorway"]

    parameters = {}

    for i, n in enumerate(list(muscle_groups.values())):
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=data[n],
                name=n,
                hovertemplate="%{y:.2f} %<extra></extra>",
                mode="lines+markers",
                line=dict(color=colors[i]),
            ),
            secondary_y=False,
        )
        x_pred = np.array(data["Time[s]"]).reshape((-1, 1))
        model = LinearRegression().fit(x_pred, y=data[n])
        y_pred = model.predict(x_pred)
        fig.add_trace(
            go.Scattergl(
                x=data["Time[s]"],
                y=y_pred,
                name="Tendance de " + n,
                mode="lines",
                line=dict(color=colors[i]),
            )
        )

        parameters[n] = (sum(y_pred) / len(y_pred), model.coef_[0])

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

    return fig, parameters


def checks(data, muscle_groups, thresholds):
    # replace the column names
    data.rename(columns=muscle_groups, inplace=True)
    # check the thresholds
    if thresholds is not None:
        if thresholds[0] is not None:
            data["Seuil 1"] = thresholds[0]
        if thresholds[1] is not None:
            data["Seuil 2"] = thresholds[1]

    return data
