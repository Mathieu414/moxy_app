import pandas as pd
import numpy as np

import base64
import io
from dash import html
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def calc_slope(x):
    slope = np.polyfit(range(len(x)), x, 1)[0]
    return slope

# set min_periods=2 to allow subsets less than 60.
# use [4::5] to select the results you need.


def df_slope(df):
    result = df.rolling(10, min_periods=2, center=True).apply(calc_slope)
    return result


def cut_pauses(df, threshold=-1.0):
    """
    Cut the pauses between the levels of the VO2 test

    Args:
        df (DataFrame): containing the data previously selected
        threshold (float, optional): Threshold for the detection of the slope. Defaults to -1.0.

    Returns:
        tuple: 
            list : contains a list of the levels detected
            str : error message
    """
    print("--cut_pauses--")
    cond = (df['Slope'] < threshold) & (df['Slope'].shift(1) >= threshold)
    slope_index = [x - 5 for x in df[cond].index.tolist()]
    if len(slope_index) > 0:

        list_levels = []

        hr_threshold = df.loc[slope_index]['HR[bpm]']
        next_hr = []
        # print(hr_threshold)
        for (value, index) in zip(hr_threshold, hr_threshold.index):

            condition_find_next_hr = (df['HR[bpm]'] > value) & (
                df['HR[bpm]'].shift(1) <= value) & (df.index > index)
            if not df[condition_find_next_hr].empty:
                next_hr.append(df[condition_find_next_hr].iloc[0])

            # put the levels detected in a list
            if len(next_hr) == 1:
                list_item = df.loc[:next_hr[0].name]
                list_item.loc[index:next_hr[0].name] = np.nan
                list_levels.append(list_item)
            else:
                list_item = df.loc[next_hr[-2].name:next_hr[-1].name]
                list_item.loc[index:next_hr[-1].name] = np.nan
                list_levels.append(list_item)

        print(list_levels)
        return (list_levels, None)
    else:
        return ([df], "Erreur : pas de pauses détectées")


def cut_begining_end(df, threshold_begining=1.0, threshold_end=-0.4):
    cond = (df['Slope'] < threshold_begining) & (
        df['Slope'].shift(1) >= threshold_begining)
    slope_index = [x for x in df[cond].index.tolist()]
    df = df.drop(df.loc[: slope_index[0]].index.tolist())
    cond = (df['Slope'] < threshold_end) & (
        df['Slope'].shift(1) >= threshold_end)
    slope_index = [x for x in df[cond].index.tolist()]
    df = df.drop(df.loc[slope_index[-1]:].index.tolist())
    return df


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


def create_figure(data, slope=True):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for n in data[1]:
        fig.add_trace(go.Scatter(
            x=data[0]["Time[s]"], y=data[0][n], name=n,  hovertemplate="%{y:.2f} %<extra></extra>", mode='lines+markers'), secondary_y=False)

    if "HR[bpm]" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["HR[bpm]"],
                                 name="HR", hovertemplate="%{y:.2f} bpm<extra></extra>", mode='lines+markers'), secondary_y=True)

    if "Seuil 1" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["Seuil 1"], line_width=3, line_dash="dash",
                                 line_color="green", name="Seuil 1"), secondary_y=True)

    if "Seuil 2" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["Seuil 2"], line_width=3, line_dash="dash",
                                 line_color="yellow", name="Seuil 2"), secondary_y=True)

    if slope:
        if "Slope" in data[0].columns:
            fig.add_trace(go.Scatter(
                x=data[0]["Time[s]"], y=data[0]["Slope"]*100, line_width=3, name="Slope"))

    fig.update_traces(marker_size=1)
    fig.update_xaxes(showgrid=False, title="Temps")
    fig.update_yaxes(title_text="Desoxygenation", secondary_y=False)
    fig.update_layout(
        clickmode='event+select',
        height=500,
        margin=dict(l=20, r=20, t=30, b=20))

    return fig


def create_filtered_figure(data, slope=True):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    data[0] = pd.concat(data[0])

    for n in data[1]:
        fig.add_trace(go.Scatter(
            x=data[0]["Time[s]"], y=data[0][n], name=n,  hovertemplate="%{y:.2f} %<extra></extra>", mode='lines+markers'), secondary_y=False)

    if "HR[bpm]" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["HR[bpm]"],
                                 name="HR", hovertemplate="%{y:.2f} bpm<extra></extra>", mode='lines+markers'), secondary_y=True)

    if "Seuil 1" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["Seuil 1"], line_width=3, line_dash="dash",
                                 line_color="green", name="Seuil 1"), secondary_y=True)

    if "Seuil 2" in data[0].columns:
        fig.add_trace(go.Scatter(x=data[0]["Time[s]"], y=data[0]["Seuil 2"], line_width=3, line_dash="dash",
                                 line_color="yellow", name="Seuil 2"), secondary_y=True)

    if slope:
        if "Slope" in data[0].columns:
            fig.add_trace(go.Scatter(
                x=data[0]["Time[s]"], y=data[0]["Slope"]*100, line_width=3, name="Slope"))

    fig.update_traces(marker_size=1)
    fig.update_xaxes(showgrid=False, title="Temps")
    fig.update_yaxes(title_text="Desoxygenation", secondary_y=False)
    fig.update_layout(
        clickmode='event+select',
        height=500,
        margin=dict(l=20, r=20, t=30, b=20))

    return fig
