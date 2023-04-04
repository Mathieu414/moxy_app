from dash_extensions.enrich import Input, Output, State, callback, ctx, no_update, MATCH, ALL, ServersideOutput, Trigger
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from scipy import signal
import pages.utils.functions as fc
import pages.utils.read_xml as read_xml
import plotly.io as pio
import re

import base64
import io


def get_store_callbacks(page, debug=True):
    @page.callback(
        [ServersideOutput('data-upload', 'data'),
         Output('seuils', 'data'),
         Output("peaks-parameters", "data")],

        [Input("test-data-upload", "contents"),
         Input("test-data-upload", "filename"),
         Input("seuil1", 'value'),
         Input("seuil2", 'value'),
         Input("clear-button", "n_clicks"),
         Input("test-choice", 'value'),
         Input("test-chart", "selectedData"),
         Input("filter-selection-button", "n_clicks"),
         Input("vo2-data", "data"),
         Input("modal_close", "n_clicks"),
         Input({'type': 'muscle-input', 'index': ALL}, 'value'),
         Input('print-pdf', 'n_clicks'),
         Input('re-render', 'n_clicks'),],

        [State("data-upload", 'data'),
         State("seuils", "data"),
         State("prominence", "value"),
         State("width", "value"),
         State("removed_width_left", "value"),
         State("removed_width_right", "value"),
         State("peaks-parameters", "data")],
        prevent_initial_call=True,
    )
    def data_upload(contents, filenames, seuil1, seuil2, clear_button, value, selectedData, filter_button, vo2_data, modal_button, modal_values, pdf_button, re_render,
                    stored_data: list, stored_seuils: list, prominence, width, removed_width_left, removed_width_right, stored_peaks_param: list):
        """
        function to modify the data in the data-upload Store component.

        Returns:
            list : 
                in [0], data-upload.data : list containing the figures data for each threshold :
                    in [0] : dataframe containing the raw data imported
                    in [1] : 
                        in [0] : list containing the different muscles registered in the modal, or just the columns names
                        in [1] : list of the initial column names, to keep the record of the moxy numbers
                    in [2] (optional) : dataframe containing the selected data from [0]
                    in [3] (optional) : dataframe containing the filtered data from [1]
                in [1], seuils.data : list containing a list of thresholds for each test
                in [2], detection-threshold.data : list containing the prominence and width for each tests
        """
        pio.templates.default = "plotly_dark_custom"

        if debug:
            print("--data-upload--")

        if (ctx.triggered_id == "test-data-upload") and (('DataAverage.xlsx' in filenames) or ('DataAverage.csv' in filenames)):

            data = []
            data.append(fc.parse_data(contents, filenames))

            moxy_numbers = []
            col_names = []
            for col in data[0].columns:
                if 'SmO2' in col:
                    if re.search("-  (\d)\[", col) is not None:
                        moxy_numbers.append(
                            re.findall("-  (\d)\[", col)[0])
                    else:
                        moxy_numbers.append("1")
                    col_names.append(col)

            # add the column names corresponding to the muscles
            data.append([col_names, moxy_numbers])

            print(data[1])

            # smooth the data
            for n in data[1][0]:
                data[0][n] = signal.savgol_filter(data[0][n], 40, 3)

            # value for the thresholds by default
            new_seuils = [None, None]

            # check if HR is present
            if "HR[bpm]" in data[0].columns:
                data[0]["HR[bpm]"] = signal.savgol_filter(
                    data[0]["HR[bpm]"], 40, 4)
                new_seuils = [None, None]

            data[0] = data[0].to_json()
            if stored_data:
                stored_data.append([data[0], data[1]])
                stored_seuils.append(new_seuils)
                stored_peaks_param.append([10, 20, 20, 20])
                return [stored_data, stored_seuils, stored_peaks_param]
            else:
                return [[[data[0], data[1]]], [new_seuils], [[8, 20, 20, 20]]]

        # if the element triggered is the modal
        if (ctx.triggered_id == "modal_close"):
            # change the column names of the base data
            col_names = dict(zip(stored_data[value][1][0], modal_values))
            stored_data[value][0] = pd.read_json(
                stored_data[value][0])
            stored_data[value][0].rename(columns=col_names, inplace=True)
            stored_data[value][0] = stored_data[value][0].to_json()

            # change the muscle names list
            for i, n in enumerate(modal_values):
                stored_data[value][1][0][i] = n

            # change the selected data column names
            if len(stored_data[value]) >= 3:
                stored_data[value][2] = pd.read_json(
                    stored_data[value][2])
                stored_data[value][2].rename(columns=col_names, inplace=True)
                stored_data[value][2] = stored_data[value][2].to_json()

            # change the filtered data column names
            if len(stored_data[value]) >= 4:
                for i, n in enumerate(stored_data[value][3]):
                    stored_data[value][3][i] = pd.read_json(
                        stored_data[value][3][i])
                    stored_data[value][3][i].rename(
                        columns=col_names, inplace=True)
                    stored_data[value][3][i] = stored_data[value][3][i].to_json()

            return [stored_data, no_update, no_update]

        if debug:
            print("valeur de seuil1")
            print(seuil1)
            print("valeur de seuil2")
            print(seuil2)

        # if the triggered element are the thresholds input
        if (ctx.triggered_id in ["seuil1", "seuil2"]) and (not all(s is None for s in (seuil1, seuil2))):
            if debug:
                print("Seuil 1 or Seuil 2 are trigered and are not None")
            df = pd.read_json(stored_data[value][0])
            df_selected = None
            df_filtered = None
            # Read the stored selected data
            if len(stored_data[value]) >= 3:
                df_selected = pd.read_json(stored_data[value][2])
            # read the stored filtered data
            if len(stored_data[value]) >= 4:
                df_filtered = stored_data[value][3]
                for n in range(len(df_filtered)):
                    df_filtered[n] = pd.read_json(df_filtered[n])

            def set_seuils(seuil, df, df_selected, df_filtered, name):
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

            df, df_selected, df_filtered = set_seuils(
                seuil1, df, df_selected, df_filtered, "Seuil 1")
            df, df_selected, df_filtered = set_seuils(
                seuil2, df, df_selected, df_filtered, "Seuil 2")

            df = df.to_json()
            stored_data[value][0] = df

            if df_selected is not None:
                df_selected = df_selected.to_json()
                stored_data[value][2] = df_selected
            if df_filtered is not None:
                for n in range(len(df_filtered)):
                    df_filtered[n] = df_filtered[n].to_json()
                stored_data[value][3] = df_filtered

            stored_seuils[value] = [seuil1, seuil2]
            return [stored_data, stored_seuils, no_update]

        if (ctx.triggered_id == "clear-button") and (clear_button > 0):
            if debug:
                print("Clearing data")
            stored_data = None
            return [stored_data, None, None]

        if ctx.triggered_id == "test-chart":
            if debug:
                print("Storing data selection")
            if selectedData and selectedData['points']:
                data_selected = pd.read_json(stored_data[value][0])
                selected_time = []
                for point in selectedData["points"]:
                    selected_time.append(point['x'])
                data_selected = data_selected.query(
                    "`Time[s]` == @selected_time")
                if vo2_data:
                    if str(value) in vo2_data.keys():
                        if debug:
                            print("synchronize vo2")
                        vo2_df = vo2_data[str(value)]
                        data_selected = fc.synchronise_moxy_vo2(
                            data_selected, pd.read_json(vo2_df))
                if len(stored_data[value]) >= 3:
                    stored_data[value][2] = data_selected.to_json()
                else:
                    stored_data[value].append(data_selected.to_json())
                return [stored_data, no_update, no_update]

        # case if the vo2 data is uploaded after the data has been selected
        if (ctx.triggered_id == "vo2-data") and (len(stored_data[value]) >= 3):
            if value is not None:
                if vo2_data:
                    data_selected = pd.read_json(stored_data[value][2])
                    if vo2_data[str(value)]:
                        if debug:
                            print("synchronize vo2")
                        vo2_df = vo2_data[str(value)]
                        data_selected = fc.synchronise_moxy_vo2(
                            data_selected, pd.read_json(vo2_df))
                        stored_data[value][2] = data_selected.to_json()

                        # If there is already filtered data, then recompute it with the vo2 data
                        if len(stored_data[value]) >= 4:
                            list_data_filtered = fc.cut_peaks(
                                data_selected, prominence=prominence, width=width, range_left=removed_width_left, range_right=removed_width_right)[0]

                            for n in range(len(list_data_filtered)):
                                list_data_filtered[n] = list_data_filtered[n].to_json(
                                )

                            stored_data[value][3] = list_data_filtered

                        return [stored_data, no_update, no_update]

        if (ctx.triggered_id == "filter-selection-button"):
            if debug:
                print("--filter_selection--")
            if value is not None:
                if len(stored_data[value]) >= 3:
                    if debug:
                        print("data selection is not empty")
                    data_selected = pd.read_json(stored_data[value][2])
                    list_data_filtered = fc.cut_peaks(
                        data_selected, prominence=prominence, width=width, range_left=removed_width_left, range_right=removed_width_right)[0]

                    for n in range(len(list_data_filtered)):
                        list_data_filtered[n] = list_data_filtered[n].to_json()

                    if len(stored_data[value]) >= 4:
                        stored_data[value][3] = list_data_filtered
                    else:
                        stored_data[value].append(list_data_filtered)

                    stored_peaks_param[value] = [
                        prominence, width, removed_width_left, removed_width_right]
                    return [stored_data, no_update, stored_peaks_param]
                else:
                    raise PreventUpdate
            else:
                raise PreventUpdate

        if (ctx.triggered_id == "print-pdf") and (value is not None):
            print("print pdf")
            pio.templates.default = "plotly_white"
            return [stored_data, no_update, no_update]

        else:
            if debug:
                print("prevent update data_upload")
            raise PreventUpdate

    @page.callback(
        Output("analytics", "data"),
        Input('test-filter-chart', 'figure'),
        Input("clear-button", "n_clicks"),
        [State('data-upload', 'data'),
         State("test-choice", 'value'),
         State("seuils", 'data')],
        prevent_initial_call=True
    )
    def compute_muscular_thresholds(fig, clear_button, stored_data, value, seuils):
        if debug:
            print("--compute_muscular_thresholds--")
            print(seuils)
        if (ctx.triggered_id == "test-filter-chart"):
            if "data" in fig.keys() and fig["data"]:
                analytics = [[], [], []]
                df_filtered = stored_data[value][3]
                for n in range(len(df_filtered)):
                    df_filtered[n] = pd.read_json(df_filtered[n])
                # check if there is any thresholds in store
                if seuils[value] != [0, 0] and seuils[value] != [None, None]:
                    print("seuils are not None")
                    threshold_muscul = [[], []]
                    df_filtered = stored_data[value][3]
                    # find the two thresholds
                    threshold_muscul[0] = fc.find_thresholds(
                        seuils[value][0], df_filtered, stored_data[value][1][0], "Seuil 1")
                    threshold_muscul[1] = fc.find_thresholds(
                        seuils[value][1], df_filtered, stored_data[value][1][0], "Seuil 2")
                    analytics[1] = threshold_muscul

                # find min and max for each muscular groups
                df_filtered_concat = pd.concat(df_filtered)
                min_max = []
                for m in stored_data[value][1][0]:
                    min_max.append(df_filtered_concat[m].min())
                analytics[0] = min_max

                # compute the time spent in the zones
                analytics[2] = fc.get_time_zones(
                    [df_filtered_concat, stored_data[value][1][0]], analytics[1])

                return analytics
            else:
                return None
        if (ctx.triggered_id == "clear-button"):
            return None

    @page.callback(
        Output("vo2-data", "data"),
        [Input("vo2-upload", "contents"),
         Input("clear-button", "n_clicks"),],
        State("test-choice", 'value'),
        State("vo2-data", "data"),
        prevent_initial_call=True
    )
    def store_xml(content, clear_button, value, stored_content):
        if debug:
            print('--store_xml--')
        if (ctx.triggered_id == "vo2-upload"):
            if content:
                content_type, content_string = content.split(",")
                decoded = base64.b64decode(content_string)
                df = read_xml.parse_xml(decoded)
                if stored_content:
                    stored_content[value] = df.to_json()
                    return stored_content
                else:
                    return {value: df.to_json()}
            else:
                raise PreventUpdate
        if (ctx.triggered_id == "clear-button"):
            return None
