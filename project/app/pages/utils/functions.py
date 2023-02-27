import pandas as pd
import numpy as np

import base64
import io
from dash import html
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from scipy.signal import find_peaks
from dtw import *


def df_find_peaks(df, prominence=8, width=20):
    """Function to find the negative peaks

    Args:
        df (DataFrame): 1 column pandas Dataframe

    Returns:
        1D array: index location of the peaks
    """
    print("--df_find_peaks--")
    return find_peaks(- df.to_numpy(), prominence=prominence, width=width)[0]


def cut_peaks(df, range=20, prominence=8, width=20):
    print("--cut_peaks--")
    peaks = df_find_peaks(df["HR[bpm]"], prominence, width)
    if len(peaks) > 0:
        list_levels = []
        if peaks[0]-range >= df.iloc[0].name:
            df.iloc[peaks[0]-range:peaks[0]+range] = np.nan
            list_levels.append(df.iloc[:peaks[0]+range])
        if len(peaks) >= 1:
            for i, v in enumerate(peaks[1:]):
                df.iloc[v-range:v+range] = np.nan
                list_levels.append(df.iloc[peaks[i]+range:v+range])
        if peaks[-1]+range <= df.iloc[-1].name:
            list_levels.append(df.iloc[peaks[-1]+range:])
        return (list_levels, str(len(list_levels)) + " paliers détectés")
    else:
        return ([df], "Erreur : pas de pauses détectées")


def parse_data(content, filename):
    """
    returns the content of a file, depending of the type of the file

    Args:
        content (str): content of the file
        filename (str): name of the file

    Returns:
        str: content of the file
    """
    content_type, content_string = content.split(",")
    decoded = base64.b64decode(content_string)
    try:
        if "xlsx" in filename:
            # Assume that the user uploaded an excel file
            return pd.read_excel(io.BytesIO(decoded))

        elif "Details.txt" in filename:
            # find the muscle groups in the file
            file = decoded.decode('utf-8')
            m = re.findall("\) - ([\w\s+]+)\n", file)
            # for i, match in enumerate(m):
            #   if any(word in match for word in re_exeptions):
            #      m.pop(i)
            t = re.findall("Start Time: (.*?)\n", file)[0]
            d = re.findall("Workout Date: (.*?)\n", file)[0]
            return [m, t, d]

    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])


def synchronise_moxy_vo2(moxy_data, vo2_df):
    # remove the line with the units
    vo2_df = vo2_df.iloc[1:]
    # transform the time into seconds
    vo2_df['Temps'] = (pd.to_datetime(
        vo2_df['Temps']) - pd.to_datetime(
        vo2_df['Temps'][1])).dt.total_seconds().round().astype(int)
    vo2_df = vo2_df.rename(
        columns={"Temps": "Time[s]"})
    # tranform the hr into numeric values
    vo2_df["Fréquence cardiaque"] = pd.to_numeric(
        vo2_df["Fréquence cardiaque"], errors='coerce')
    # dataframe to numpy
    x = vo2_df["Fréquence cardiaque"].to_numpy()
    y = moxy_data["HR[bpm]"].to_numpy()
    # using the dtw library to match the datasets
    alignment = warp(dtw(x, y), index_reference=True)
    # replace the index with the VO2 values
    path = []
    for i, index_moxy in enumerate(alignment):
        path.append([float(vo2_df.iloc[i]["Consommation d'Oxygène"]),
                     x[i],
                     moxy_data.iloc[index_moxy]["Time[s]"]])
    # set the index, and remove the duplicates
    df = pd.DataFrame(
        path, columns=["VO2", "FC", "Time[s]"]).set_index("Time[s]")
    df = df[~df.index.duplicated(keep='first')]
    # merge the two dfs
    moxy_data = moxy_data.merge(df, on='Time[s]')
    return moxy_data


def get_time_zones(data, seuils_muscu):
    print("--get-time-zones--")
    if len(seuils_muscu) > 0:
        time_z1 = []
        time_z2 = []
        time_z3 = []
        for i, m in enumerate(data[1]):
            print("Seuils Musculaires : ", seuils_muscu)
            if len(seuils_muscu[0]) > 0:
                print(i)
                print(data[0][m][data[0][m] < seuils_muscu[0][i]])
                time_z1.append(
                    len(data[0][m][data[0][m] > seuils_muscu[0][i]].index.tolist()))
            if len(seuils_muscu[1]) > 0:
                time_z2.append(len(data[0][m][(data[0][m] <= seuils_muscu[0][i]) & (
                    data[0][m] > seuils_muscu[1][i])].index.tolist()))
                time_z3.append(
                    len(data[0][m][data[0][m] < seuils_muscu[1][i]].index.tolist()))
        print(time_z1)
        print(time_z2)
        print(time_z3)
        return ([time_z1, time_z2, time_z3])
    else:
        return []
