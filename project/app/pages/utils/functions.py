import pandas as pd
import numpy as np

import base64
import io
from dash import html
import re
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


def cut_peaks(df, range_right=20, range_left=20, prominence=8, width=20):
    """Removes the data around the peaks detected by the find_peaks function

    Args:
        df (pandas Dataframe): Dataframe containing the data to cut
        range (int, optional): length of data to remove around the peak detected. Defaults to 20.
        prominence (int, optional): minimal peak heigth. Defaults to 8.
        width (int, optional): minimal peak width. Defaults to 20.

    Returns:
        tuple : a list containing the dataframe with the data around the peaks removed (or not), and a string
            with the corresponding success or error message
    """
    print("--cut_peaks--")
    peaks = df_find_peaks(df["HR[bpm]"], prominence, width)
    print(peaks)
    if len(peaks) > 0:
        list_levels = []
        # check for index problems at the begining
        if (peaks[0]-range_left) >= 0:
            df.iloc[peaks[0]-range_left:peaks[0]+range_right] = np.nan
            list_levels.append(df.iloc[:peaks[0]+range_right])
        if len(peaks) >= 1:
            for i, v in enumerate(peaks[1:]):
                df.iloc[v-range_left:v+range_right] = np.nan
                list_levels.append(df.iloc[peaks[i]+range_right:v+range_right])
        # check for index problems at the end
        if peaks[-1]+range_right <= df.iloc[-1].name:
            list_levels.append(df.iloc[peaks[-1]+range_right:])
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
        if "csv" in filename:
            return pd.read_csv(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])


def synchronise_moxy_vo2(moxy_data, vo2_df):
    """Uses the dtw library to synchronise the data from the moxy device and the data from the VO2 device

    Args:
        moxy_data (pandas Dataframe): moxy data
        vo2_df (pandas Dataframe): vo2 data

    Returns:
        pandas Dataframe: moxy data with the synchronised vo2 data in it
    """
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
    print(alignment)
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
    df = df.iloc[1:]
    # merge the two dfs
    moxy_data = moxy_data.merge(df, how='left', on='Time[s]')
    return moxy_data


def get_time_zones(data, seuils_muscu):
    """get the time spent in the difference muscular zones

    Args:
        data (list): list containing the data : in [0] a dataframe with the data, in [1] the muscle groups
        seuils_muscu (list): list containing the different thresholds for the muscles

    Returns:
        list: list with zone times
    """
    print("--get-time-zones--")
    if len(seuils_muscu) > 0:
        time_z1 = []
        time_z2 = []
        time_z3 = []
        for i, m in enumerate(data[1]):
            if len(seuils_muscu[0]) > 0:
                time_z1.append(
                    len(data[0][m][data[0][m] > seuils_muscu[0][i]].index.tolist()))
            if len(seuils_muscu[1]) > 0:
                time_z2.append(len(data[0][m][(data[0][m] <= seuils_muscu[0][i]) & (
                    data[0][m] > seuils_muscu[1][i])].index.tolist()))
                time_z3.append(
                    len(data[0][m][data[0][m] < seuils_muscu[1][i]].index.tolist()))
        return ([time_z1, time_z2, time_z3])
    else:
        return []
