import pandas as pd
import numpy as np

import base64
import io
from dash_extensions.enrich import html
from scipy.signal import find_peaks
from dtw import *
from scipy import optimize
import re


def df_find_peaks(df, prominence=8, width=20):
    """Function to find the negative peaks

    Args:
        df (DataFrame): 1 column pandas Dataframe

    Returns:
        1D array: index location of the peaks
    """
    print("--df_find_peaks--")
    return find_peaks(-df.to_numpy(), prominence=prominence, width=width)[0]


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
    df = df.copy(deep=True)
    peaks = df_find_peaks(df["HR[bpm]"], prominence, width)
    print(peaks)
    if len(peaks) > 0:
        list_levels = []
        # check for index problems at the begining
        if (peaks[0] - range_left) >= 0:
            df.iloc[peaks[0] - range_left : peaks[0] + range_right] = np.nan
            list_levels.append(df.iloc[: peaks[0] + range_right])
        if len(peaks) >= 1:
            for i, v in enumerate(peaks[1:]):
                df.iloc[v - range_left : v + range_right] = np.nan
                list_levels.append(df.iloc[peaks[i] + range_right : v + range_right])
        # check for index problems at the end
        if peaks[-1] + range_right <= df.iloc[-1].name:
            list_levels.append(df.iloc[peaks[-1] + range_right :])
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
    print("--parse_data--")
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
    if "VO2" in moxy_data.columns:
        moxy_data = moxy_data.drop(["VO2", "FC"], axis=1)
    print(moxy_data.columns)
    # transform the time into seconds
    vo2_df["Temps"] = (
        (pd.to_datetime(vo2_df["Temps"]) - pd.to_datetime(vo2_df["Temps"][1]))
        .dt.total_seconds()
        .round()
        .dropna()
        .astype(int)
    )
    vo2_df = vo2_df.rename(columns={"Temps": "Time[s]"})
    # tranform the hr into numeric values
    vo2_df["Fréquence cardiaque"] = pd.to_numeric(
        vo2_df["Fréquence cardiaque"], errors="coerce"
    )
    # dataframe to numpy
    x = vo2_df["Fréquence cardiaque"].to_numpy()
    y = moxy_data["HR[bpm]"].to_numpy().astype(int)
    # using the dtw library to match the datasets
    alignment = warp(dtw(x, y), index_reference=True)
    # replace the index with the VO2 values
    path = []
    for i, index_moxy in enumerate(alignment):
        path.append(
            [
                float(vo2_df.iloc[i]["Consommation d'Oxygène"]),
                x[i],
                moxy_data.iloc[index_moxy]["Time[s]"],
            ]
        )
    # set the index, and remove the duplicates
    df = pd.DataFrame(path, columns=["VO2", "FC", "Time[s]"]).set_index("Time[s]")
    df = df[~df.index.duplicated(keep="first")]
    df = df.iloc[1:]
    # merge the two dfs
    moxy_data = moxy_data.merge(df, how="left", on="Time[s]")
    return moxy_data


def get_time_zones(data, muscle_groups, thresholds_muscu):
    """get the time spent in the difference muscular zones

    Args:
        data (list): list containing the data : in [0] a dataframe with the data, in [1] the muscle groups
        thresholds_muscu (list): list containing the different thresholds for the muscles

    Returns:
        list: list with zone times
    """
    print("--get-time-zones--")
    if len(thresholds_muscu) > 0:
        print(thresholds_muscu)
        time_z1 = []
        time_z2 = []
        time_z3 = []
        for i, m in enumerate(muscle_groups):
            if len(thresholds_muscu[0]) > 0:
                time_z1.append(
                    len(data[m][data[m] > thresholds_muscu[0][i]].index.tolist())
                )
            if len(thresholds_muscu[1]) > 0:
                if len(thresholds_muscu[0]) > 0:
                    time_z2.append(
                        len(
                            data[m][
                                (data[m] <= thresholds_muscu[0][i])
                                & (data[m] > thresholds_muscu[1][i])
                            ].index.tolist()
                        )
                    )
                time_z3.append(
                    len(data[m][data[m] < thresholds_muscu[1][i]].index.tolist())
                )
        return [time_z1, time_z2, time_z3]
    else:
        return []


def segments_fit(X, Y, maxcount):
    xmin = X.min()
    xmax = X.max()

    n = len(X)

    AIC_ = float("inf")
    BIC_ = float("inf")
    r_ = None

    for count in range(1, maxcount + 1):
        seg = np.full(count - 1, (xmax - xmin) / count)

        px_init = np.r_[np.r_[xmin, seg].cumsum(), xmax]
        py_init = np.array(
            [Y[np.abs(X - x) < (xmax - xmin) * 0.1].mean() for x in px_init]
        )

        def func(p):
            seg = p[: count - 1]
            py = p[count - 1 :]
            px = np.r_[np.r_[xmin, seg].cumsum(), xmax]
            return px, py

        def err(p):  # This is RSS / n
            px, py = func(p)
            Y2 = np.interp(X, px, py)
            return np.mean((Y - Y2) ** 2)

        r = optimize.minimize(err, x0=np.r_[seg, py_init], method="Nelder-Mead")

        # Compute AIC/ BIC.
        AIC = n * np.log10(err(r.x)) + 4 * count
        BIC = n * np.log10(err(r.x)) + 2 * count * np.log(n)

        if (BIC < BIC_) & (AIC < AIC_):  # Continue adding complexity.
            r_ = r
            AIC_ = AIC
            BIC_ = BIC
        else:  # Stop.
            count = count - 1
            break

    return func(r_.x)  # Return the last (n-1)


def find_thresholds(
    seuil: int,
    df_filtered: list,
    muscle_groups: list,
    threshold_name: str,
    remove_range=5,
) -> list:
    """find the muscle threshold corresponding to the HR threshold

    Args:
        seuil (int): HR threshold
        df_filtered (list of pd.Dataframe): levels of the test
        muscle_groups (dict): dictionnary containing the names of the muscle groups
        threshold_name (string): name of the target column corresponding with the threshold number
        remove_range (int, optional): amount of points considered around the matching value to compute the threshold. Defaults to 5.

    Returns:
        list: muscle threshold values corresponding to the given HR threshold
    """
    threshold_muscle = []
    if (seuil is not None) and (seuil != 0):
        print("compute the ", threshold_name)
        # iterate over the levels of the test
        for n in range(len(df_filtered)):
            cond = (df_filtered[n]["HR[bpm]"] > seuil) & (
                df_filtered[n]["HR[bpm]"].shift(1) <= seuil
            )
            if not df_filtered[n][cond].empty:
                print(threshold_name + " found")
                indexes = df_filtered[n][cond].index.tolist()
                # store the 10 points around the first occurence matching the condition
                target_muscul = df_filtered[n].loc[
                    indexes[0] - remove_range : indexes[0] + remove_range
                ]
                # iterate over the muscle groups, and do the mean of the matching data
                for m in muscle_groups.keys():
                    threshold_muscle.append(target_muscul[m].mean())
                # the first occurence is the relevant one, no need to go further
                break
    return threshold_muscle
