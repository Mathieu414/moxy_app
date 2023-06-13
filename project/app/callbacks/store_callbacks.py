from dash_extensions.enrich import (
    Input,
    Output,
    State,
    ctx,
    no_update,
    ServersideOutput,
    html,
)
from dash.exceptions import PreventUpdate
from dash import ALL
import pandas as pd
import numpy as np
from scipy import signal
import utils.functions as fc
import utils.read_xml as read_xml
import plotly.io as pio
import re

import base64


def get_store_callbacks(page, debug=True):
    @page.callback(
        [
            ServersideOutput("raw-data", "data"),
        ],
        [
            Input("test-data-upload", "contents"),
            Input("test-data-upload", "filename"),
            Input("clear-button", "n_clicks"),
        ],
        [State("raw-data", "data")],
        prevent_initial_call=True,
    )
    def raw_data_upload(contents, filenames, clear, stored_raw_data):
        if (ctx.triggered_id == "test-data-upload") and (
            ("xlsx" in filenames) or ("csv" in filenames)
        ):
            return store_raw_data(
                contents=contents, filenames=filenames, stored_raw_data=stored_raw_data
            )
        if ctx.triggered_id == "clear-button":
            return None

    @page.callback(
        [
            Output("muscle-groups", "data"),
        ],
        [
            Input("raw-data", "data"),
            Input("clear-button", "n_clicks"),
            Input("modal_close", "n_clicks"),
        ],
        [
            State("muscle-groups", "data"),
            State({"type": "muscle-input", "index": ALL}, "value"),
            State("test-choice", "value"),
        ],
        prevent_initial_call=True,
    )
    def store_muscle_groups(
        stored_raw_data, clear, modal_button, stored_muscle_groups, modal_values, value
    ):
        """Stores muscle groups data

        Returns:
            list : Muscle groups data, each element of the list consiting of :
                [0] : dictionnary containing the initial column names as a key, and the new ones as a value.
                [1] : list of the corresponding moxy numbers
        """
        if ctx.triggered_id == "raw-data":
            moxy_numbers = []
            col_names = []
            for col in stored_raw_data[-1].columns:
                if "SmO2" in col:
                    if re.search("-  (\d)\[", col) is not None:
                        moxy_numbers.append(re.findall("-  (\d)\[", col)[0])
                    else:
                        moxy_numbers.append("1")
                    col_names.append(col)

            # create a dictionary with initial column values associated with modified column values
            col_names = dict(zip(col_names, col_names))

            # add the column names corresponding to the muscles
            if stored_muscle_groups is not None:
                stored_muscle_groups.append([col_names, moxy_numbers])
                return stored_muscle_groups
            else:
                return [[col_names, moxy_numbers]]

        if ctx.triggered_id == "modal_close":
            # change the muscle names list
            for k, v in zip(stored_muscle_groups[value][0].keys(), modal_values):
                print(k, v)
                stored_muscle_groups[value][0][k] = v
            return stored_muscle_groups

        if ctx.triggered_id == "clear-button":
            return None

    @page.callback(
        [
            Output("thresholds", "data"),
        ],
        [
            Input("raw-data", "data"),
            Input("threshold1", "value"),
            Input("threshold2", "value"),
            Input("clear-button", "n_clicks"),
        ],
        [
            State("test-choice", "value"),
            State("thresholds", "data"),
        ],
        prevent_initial_call=True,
    )
    def set_thresholds(
        raw_data, threshold1, threshold2, clear, value, stored_thresholds
    ):
        if debug:
            print("--set_thresholds--")

        # if it is first import, set the thresholds to None
        if ctx.triggered_id == "raw-data":
            if stored_thresholds is not None:
                stored_thresholds.append([None, None])
                return stored_thresholds
            else:
                return [[None, None]]

        if (ctx.triggered_id == "threshold1") and value is not None:
            stored_thresholds[value][0] = threshold1
            return stored_thresholds

        if (ctx.triggered_id == "threshold2") and value is not None:
            stored_thresholds[value][1] = threshold2
            return stored_thresholds

        if ctx.triggered_id == "clear-button":
            return None

        else:
            raise PreventUpdate

    @page.callback(
        [
            Output("peaks-parameters", "data"),
        ],
        [
            Input("raw-data", "data"),
            Input("clear-button", "n_clicks"),
            Input("filter-selection-button", "n_clicks"),
        ],
        [
            State("peaks-parameters", "data"),
            State("prominence", "value"),
            State("width", "value"),
            State("removed_width_left", "value"),
            State("removed_width_right", "value"),
            State("test-choice", "value"),
        ],
        prevent_initial_call=True,
    )
    def store_peak_parameters(
        stored_raw_data,
        clear,
        n_clicks,
        stored_peaks_parameters,
        prominence,
        width,
        removed_width_left,
        removed_width_right,
        value,
    ):
        if ctx.triggered_id == "raw-data":
            if stored_peaks_parameters is not None:
                stored_peaks_parameters.append([8, 20, 30, 70])
                return stored_peaks_parameters
            else:
                return [[8, 20, 30, 70]]

        if ctx.triggered_id == "filter-selection-button":
            stored_peaks_parameters[value] = [
                prominence,
                width,
                removed_width_left,
                removed_width_right,
            ]

        if ctx.triggered_id == "clear-button":
            return None

        else:
            raise PreventUpdate

    @page.callback(
        [
            ServersideOutput("selected-data", "data"),
        ],
        [
            Input("global-analysis-button", "n_clicks"),
            Input("clear-button", "n_clicks"),
            Input("vo2-data", "data"),
        ],
        [
            State("raw-data", "data"),
            State("selected-data", "data"),
            State("test-chart", "selectedData"),
            State("test-choice", "value"),
        ],
        prevent_initial_call=True,
    )
    def store_selected_data_global_analysis(
        btn,
        clear,
        vo2_data,
        stored_raw_data,
        stored_selected_data,
        selected_data,
        value,
    ):
        """
        Callback to handle the data selection in case of the global analysis. Can be triggered by the global-analysis-button, by the VO2 data import
        or by the clear-button.
        """
        if debug:
            print("--store_selected_data--")

        if ctx.triggered_id == "global-analysis-button" and selected_data is not None:
            return chart_selection(
                selected_data=selected_data,
                stored_selected_data=stored_selected_data,
                raw_data=stored_raw_data,
                value=value,
                vo2_data=vo2_data,
            )

        if (
            ctx.triggered_id == "vo2-data"
            and stored_selected_data is not None
            and (value in stored_selected_data)
        ):
            print("synchronise VO2")
            stored_selected_data[value] = fc.synchronise_moxy_vo2(
                stored_selected_data[value], vo2_data[value]
            )
            return stored_selected_data

        if ctx.triggered_id == "clear-button":
            return None

        else:
            raise PreventUpdate

    @page.callback(
        [
            ServersideOutput("filtered-data", "data"),
            Output("div-error-filter", "children"),
        ],
        [
            Input("filter-selection-button", "n_clicks"),
            Input("clear-button", "n_clicks"),
            Input("selected-data", "data"),
        ],
        [
            State("filtered-data", "data"),
            State("test-choice", "value"),
            State("prominence", "value"),
            State("width", "value"),
            State("removed_width_left", "value"),
            State("removed_width_right", "value"),
        ],
        prevent_initial_call=True,
    )
    def filter_data(
        filter_btn,
        clear,
        stored_selected_data,
        stored_filtered_data,
        value,
        prominence,
        width,
        removed_width_left,
        removed_width_right,
    ):
        """
        Callback to handle the filtering of the data. This callback is triggered either when the user clicks on the filtering button,
        or when new selected-data is produced. This last case occurs typically when the user imports VO2 data.
        There is also an validation message, but only for the button case.
        """
        if debug:
            print("--filter_selection--")

        if ctx.triggered_id == "filter-selection-button" or (
            ctx.triggered_id == "selected-data"
            and stored_filtered_data is not None
            and value in stored_filtered_data
        ):
            if value in stored_selected_data:
                if debug:
                    print("data selection is not empty")
                data_selected = stored_selected_data[value]
                (list_data_filtered, message) = fc.cut_peaks(
                    data_selected,
                    prominence=prominence,
                    width=width,
                    range_left=removed_width_left,
                    range_right=removed_width_right,
                )

                error_div = None

                if ctx.triggered_id == "filter-selection-button":
                    error_div = set_error_message_filter(
                        value,
                        data=data_selected,
                        message=message,
                        result=list_data_filtered,
                    )

                # store the values as a dictionnary
                if stored_filtered_data is None:
                    return [{value: list_data_filtered}, error_div]
                else:
                    stored_filtered_data[value] = list_data_filtered
                    return [stored_filtered_data, error_div]
            else:
                raise PreventUpdate

        if ctx.triggered_id == "clear-button":
            return [None, None]

        else:
            raise PreventUpdate

    @page.callback(
        Output("analytics", "data"),
        [
            Input("test-filter-chart", "figure"),
            Input("clear-button", "n_clicks"),
        ],
        [
            State("filtered-data", "data"),
            State("muscle-groups", "data"),
            State("test-choice", "value"),
            State("thresholds", "data"),
        ],
        prevent_initial_call=True,
    )
    def compute_analytics_data(
        fig, clear_button, stored_filtered_data, muscle_groups, value, thresholds
    ):
        if debug:
            print("--compute_muscular_thresholds--")
            print(thresholds)
        if ctx.triggered_id == "test-filter-chart":
            if "data" in fig.keys() and fig["data"]:
                analytics = [[], [], []]
                df_filtered = stored_filtered_data[value]
                # check if there is any thresholds in store
                if thresholds[value] != [0, 0] and thresholds[value] != [None, None]:
                    print("thresholds are not None")
                    threshold_muscul = [[], []]
                    # find the two thresholds
                    threshold_muscul[0] = fc.find_thresholds(
                        thresholds[value][0],
                        df_filtered,
                        muscle_groups[value][0],
                        "Seuil 1",
                    )
                    threshold_muscul[1] = fc.find_thresholds(
                        thresholds[value][1],
                        df_filtered,
                        muscle_groups[value][0],
                        "Seuil 2",
                    )
                    analytics[1] = threshold_muscul

                # find min and max for each muscular groups
                df_filtered_concat = pd.concat(df_filtered)
                min_max = []
                for m in muscle_groups[value][0].keys():
                    min_max.append(df_filtered_concat[m].min())
                analytics[0] = min_max

                """ # compute the time spent in the zones
                analytics[2] = fc.get_time_zones(
                    df_filtered_concat,
                    list(muscle_groups[value][0].keys()),
                    analytics[1],
                ) """

                return analytics
            else:
                return None
        if ctx.triggered_id == "clear-button":
            return None
        else:
            raise PreventUpdate

    @page.callback(
        ServersideOutput("vo2-data", "data"),
        [
            Input("vo2-upload", "contents"),
            Input("clear-button", "n_clicks"),
        ],
        [
            State("test-choice", "value"),
            State("vo2-data", "data"),
        ],
        prevent_initial_call=True,
    )
    def store_xml(content, clear_button, value, stored_content):
        if debug:
            print("--store_xml--")
        if ctx.triggered_id == "vo2-upload":
            if content:
                content_type, content_string = content.split(",")
                decoded = base64.b64decode(content_string)
                df = read_xml.parse_xml(decoded)
                if stored_content:
                    stored_content[value] = df
                    return stored_content
                else:
                    return {value: df}
            else:
                raise PreventUpdate
        if ctx.triggered_id == "clear-button":
            return None

    @page.callback(
        Output("test-data-upload", "contents"),
        Output("test-data-upload", "filename"),
        Input("clear-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_upload(n):
        return None, None

    @page.callback(
        Output("analysis-type", "data"),
        [
            Input("global-analysis-button", "n_clicks"),
            Input("local-analysis-button", "n_clicks"),
            Input("clear-button", "n_clicks"),
        ],
        [
            State("test-chart", "selectedData"),
            State("test-choice", "value"),
            State("analysis-type", "data"),
            State("selected-data", "data"),
            State("trend-data", "data"),
        ],
        prevent_initial_call=True,
    )
    def set_analysis_type(
        global_click,
        local_click,
        clear,
        selected_data,
        value,
        stored_analysis_type,
        stored_selected_data,
        stored_trend_data,
    ):
        if (
            ctx.triggered_id == "global-analysis-button"
            and (
                selected_data is not None
                or (stored_selected_data is not None and value in stored_selected_data)
            )
        ) or (
            ctx.triggered_id == "local-analysis-button"
            and (
                selected_data is not None
                or (stored_trend_data is not None and value in stored_trend_data)
            )
        ):
            if stored_analysis_type is None:
                return {value: ctx.triggered_id}
            else:
                stored_analysis_type[value] = ctx.triggered_id
                return stored_analysis_type
        if ctx.triggered_id == "clear-button":
            return None
        else:
            raise PreventUpdate

    @page.callback(
        [
            Output("pio-template", "data"),
        ],
        [
            Input("test-header-div", "children"),
            Input("print-pdf", "n_clicks"),
        ],
    )
    def update_template(c, n):
        if ctx.triggered_id == "print-pdf":
            print("print pdf")
            return "plotly_white"

        else:
            return "plotly_dark_custom"

    @page.callback(
        [
            ServersideOutput("trend-data", "data"),
        ],
        [
            Input("local-analysis-button", "n_clicks"),
            Input("clear-button", "n_clicks"),
        ],
        [
            State("raw-data", "data"),
            State("selected-data", "data"),
            State("test-chart", "selectedData"),
            State("test-choice", "value"),
        ],
        prevent_initial_call=True,
    )
    def store_selected_data_global_analysis(
        btn,
        clear,
        stored_raw_data,
        stored_selected_data,
        selected_data,
        value,
    ):
        if debug:
            print("--store_trend_data--")

        if ctx.triggered_id == "local-analysis-button" and selected_data is not None:
            return chart_selection(
                selected_data=selected_data,
                stored_selected_data=stored_selected_data,
                raw_data=stored_raw_data,
                value=value,
                vo2_data=None,
            )

        if ctx.triggered_id == "clear-button":
            return None

        else:
            raise PreventUpdate


def store_raw_data(contents, filenames, stored_raw_data: list):
    print("test-data-upload")

    data = fc.parse_data(contents, filenames)

    # find the columns corresponding to the muscle groups
    muscle_col_names = []
    for col in data.columns:
        if "SmO2" in col:
            muscle_col_names.append(col)

    # smooth the data
    for n in muscle_col_names:
        data[n] = signal.savgol_filter(data[n], 40, 3)

    # check if HR is present
    if "HR[bpm]" in data.columns:
        data["HR[bpm]"] = signal.savgol_filter(data["HR[bpm]"], 40, 4)

    if stored_raw_data:
        stored_raw_data.append(data)
        return stored_raw_data
    else:
        return [data]


def condition_modal_close(
    modal_values,
    stored_data,
    value,
):
    print("modal_close")

    # change the column names of the base data
    col_names = dict(zip(stored_data[value][1][0], modal_values))
    stored_data[value][0] = stored_data[value][0]
    stored_data[value][0].rename(columns=col_names, inplace=True)
    stored_data[value][0] = stored_data[value][0]

    # change the muscle names list
    for i, n in enumerate(modal_values):
        stored_data[value][1][0][i] = n

    # change the selected data column names
    if len(stored_data[value]) >= 3:
        stored_data[value][2] = stored_data[value][2]
        stored_data[value][2].rename(columns=col_names, inplace=True)
        stored_data[value][2] = stored_data[value][2]

    # change the filtered data column names
    if len(stored_data[value]) >= 4:
        for i, n in enumerate(stored_data[value][3]):
            stored_data[value][3][i] = stored_data[value][3][i]
            stored_data[value][3][i].rename(columns=col_names, inplace=True)
            stored_data[value][3][i] = stored_data[value][3][i]

    return [stored_data, no_update, no_update]


def condition_seuil_input(
    stored_data, value, threshold1, threshold2, stored_thresholds
):
    df = stored_data[value][0]
    df_selected = None
    df_filtered = None
    # Read the stored selected data
    if len(stored_data[value]) >= 3:
        df_selected = stored_data[value][2]
    # read the stored filtered data
    if len(stored_data[value]) >= 4:
        df_filtered = stored_data[value][3]
        for n in range(len(df_filtered)):
            df_filtered[n] = df_filtered[n]

    def set_thresholds(seuil, df, df_selected, df_filtered, name):
        if (seuil is not None) and (seuil != 0):
            df[name] = seuil
            if df_selected is not None:
                df_selected[name] = seuil
            if df_filtered is not None:
                for n in range(len(df_filtered)):
                    df_filtered[n][name] = seuil
        else:
            if name in df.columns:
                df = df.drop(columns=name)
            if (df_selected is not None) and (name in df_selected.columns):
                df_selected = df_selected.drop(name)
            if (df_filtered is not None) and (name in df_filtered[0].columns):
                for n in range(len(df_filtered)):
                    df_filtered[n] = df_filtered[n].drop(name)

        return df, df_selected, df_filtered

    df, df_selected, df_filtered = set_thresholds(
        threshold1, df, df_selected, df_filtered, "Seuil 1"
    )
    df, df_selected, df_filtered = set_thresholds(
        threshold2, df, df_selected, df_filtered, "Seuil 2"
    )

    df = df
    stored_data[value][0] = df

    if df_selected is not None:
        df_selected = df_selected
        stored_data[value][2] = df_selected
    if df_filtered is not None:
        stored_data[value][3] = df_filtered

    stored_thresholds[value] = [threshold1, threshold2]
    return [stored_data, stored_thresholds, no_update]


def chart_selection(
    selected_data, stored_selected_data, raw_data: list, value, vo2_data: pd.DataFrame
):
    if selected_data and selected_data["points"]:
        data = raw_data[value]
        selected_time = []
        for point in selected_data["points"]:
            selected_time.append(point["x"])
        data = data.query("`Time[s]` == @selected_time")
        if vo2_data is not None:
            if value in vo2_data.keys():
                print("synchronize vo2")
                vo2_df = vo2_data[value]
                data = fc.synchronise_moxy_vo2(data, vo2_df)
        if stored_selected_data is None:
            return {value: data}
        else:
            stored_selected_data[value] = data
            return stored_selected_data


def set_error_message_filter(value, data, message, result):
    if value is not None:
        if data is not None:
            if message is not None:
                if len(result) == 1:
                    return html.P(message, className="error")
                if len(result) > 1:
                    return html.P(message, className="success")
                else:
                    return None
            else:
                return None
        else:
            return html.P("Pas de données selectionnées", className="error")
    else:
        return html.P("Pas de test selectionné", className="error")
