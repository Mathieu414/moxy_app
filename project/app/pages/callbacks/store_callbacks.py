from dash import Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from scipy import signal
import pages.utils.functions as fc
import pages.utils.read_xml as read_xml

import base64
import io


def get_store_callbacks(debug=True):
    @callback(
        [Output('data-upload', 'data'),
         Output('seuils', 'data'),
         Output("peaks-parameters", "data")],
        [Input("test-upload", "contents"),
         Input("test-upload", "filename"),
         Input("seuil1", 'value'),
         Input("seuil2", 'value'),
         Input("clear-button", "n_clicks"),
         Input("test-choice", 'value'),
         Input("test-chart", "selectedData"),
         Input("filter-selection-button", "n_clicks"),
         Input("vo2-data", "data")],
        [State("data-upload", 'data'),
         State("seuils", "data"),
         State("prominence", "value"),
         State("width", "value"),
         State("peaks-parameters", "data")],
        prevent_initial_call=True,
    )
    def data_upload(contents, filenames, seuil1, seuil2, clear_button, value, selectedData, filter_button, vo2_data,
                    stored_data, stored_seuils, prominence, width, stored_peaks_param):
        """
        function to modify the data in the data-upload Store component.

        Returns:
            list : 
                in [0], data-upload.data : list containing the figures data for each threshold :
                    in [0] : dataframe containing the raw data imported
                    in [1] : 
                        in [0] : list containing the different muscles contained in the "Details.txt" file
                        in [1] : string containing the start time of the record
                        in [2] : string containing the date
                    (optional) in [2] : dataframe containing the selected data from [0]
                    (optional) in [3] : dataframe containing the filtered data from [1]
                in [1], seuils.data : list containing a list of thresholds for each test
                in [2], detection-threshold.data : list containing the prominence and width for each tests
        """
        if debug:
            print("--data-upload--")

        if (ctx.triggered_id == "test-upload") and ('Details.txt' in filenames) and ('DataAverage.xlsx' in filenames):
            t_id = filenames.index('Details.txt')
            x_id = filenames.index('DataAverage.xlsx')
            data = []
            for content, filename in zip(contents, filenames):
                data.append(fc.parse_data(content, filename))

            smo_cols = [col for col in data[x_id].columns if 'SmO2' in col]

            col_names = dict(zip(smo_cols, data[t_id][0]))

            data[x_id].rename(columns=col_names, inplace=True)

            # check if the elements are in the right order
            if t_id == 0:
                data[0], data[1] = data[1], data[0]
            data[0].replace(0, np.nan, inplace=True)

            # smooth the data
            for n in data[1][0]:
                data[0][n] = signal.savgol_filter(data[0][n], 40, 3)

            # value for the thresholds by default
            new_seuils = [None, None]

            # check if HR is present
            if "HR[bpm]" in data[0].columns:
                data[0]["HR[bpm]"] = signal.savgol_filter(
                    data[0]["HR[bpm]"], 40, 4)
                new_seuils = [0, 0]

            data[0] = data[0].to_json()
            if stored_data:
                stored_data.append([data[0], data[1]])
                stored_seuils.append(new_seuils)
                stored_peaks_param.append([8, 20])
                return [stored_data, stored_seuils, stored_peaks_param]
            else:
                return [[[data[0], data[1]]], [new_seuils], [[8, 20]]]

        if debug:
            print("valeur de seuil1")
            print(seuil1)
            print("valeur de seuil2")
            print(seuil2)

        if (ctx.triggered_id in ["seuil1", "seuil2"]) and (not all(s is None for s in (seuil1, seuil2))):
            if debug:
                print("Seuil 1 or Seuil 2 are trigered and are not None")
            df = pd.read_json(stored_data[value][0])
            df_selected = None
            df_filtered = None
            if len(stored_data[value]) >= 3:
                df_selected = pd.read_json(stored_data[value][2])
            if len(stored_data[value]) >= 4:
                df_filtered = stored_data[value][3]
                for n in range(len(df_filtered)):
                    df_filtered[n] = pd.read_json(df_filtered[n])
            if (seuil1 is not None) and (seuil1 != 0):
                df["Seuil 1"] = seuil1
                if df_selected is not None:
                    df_selected["Seuil 1"] = seuil1
                if df_filtered is not None:
                    for n in range(len(df_filtered)):
                        df_filtered[n]["Seuil 1"] = seuil1
            if (seuil2 is not None) and (seuil2 != 0):
                if debug:
                    print("seuil2 is not None and not 0")
                df["Seuil 2"] = seuil2
                if df_selected is not None:
                    df_selected["Seuil 2"] = seuil2
                if df_filtered is not None:
                    for n in range(len(df_filtered)):
                        df_filtered[n]["Seuil 2"] = seuil2
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
                        [vo2_df, _] = vo2_data[str(value)]
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
                        [vo2_df, _] = vo2_data[str(value)]
                        data_selected = fc.synchronise_moxy_vo2(
                            data_selected, pd.read_json(vo2_df))

                        if len(stored_data[value]) >= 4:
                            list_data_filtered = fc.cut_peaks(
                                data_selected, prominence=prominence, width=width)[0]

                            for n in range(len(list_data_filtered)):
                                list_data_filtered[n] = list_data_filtered[n].to_json(
                                )

                            stored_data[value][3] = list_data_filtered

                        stored_data[value][2] = data_selected.to_json()
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
                        data_selected, prominence=prominence, width=width)[0]

                    for n in range(len(list_data_filtered)):
                        list_data_filtered[n] = list_data_filtered[n].to_json()

                    if len(stored_data[value]) >= 4:
                        stored_data[value][3] = list_data_filtered
                    else:
                        stored_data[value].append(list_data_filtered)

                    stored_peaks_param[value] = [prominence, width]
                    return [stored_data, no_update, stored_peaks_param]
                else:
                    raise PreventUpdate
            else:
                raise PreventUpdate

        else:
            if debug:
                print("prevent update data_upload")
            raise PreventUpdate

    @callback(
        Output("analytics", "data"),
        Input('test-filter-chart', 'figure'),
        [State('data-upload', 'data'),
         State("test-choice", 'value'),
         State("seuils", 'data')],
        prevent_initial_call=True
    )
    def compute_muscular_thresholds(fig, stored_data, value, seuils):
        if debug:
            print("--compute_muscular_thresholds--")
        if "data" in fig.keys():
            analytics = [[], []]
            df_filtered = stored_data[value][3]
            for n in range(len(df_filtered)):
                df_filtered[n] = pd.read_json(df_filtered[n])
            # check if there is any thresholds in store
            if seuils[value] != [0, 0]:
                print("seuils are not None")
                threshold_muscul = [[], []]
                df_filtered = stored_data[value][3]
                if seuils[value][0] > 0:
                    if debug:
                        print("compute the first threshod")
                    # iterate over the levels of the test
                    for n in range(len(df_filtered)):
                        cond = (df_filtered[n]["HR[bpm]"] > df_filtered[n]["Seuil 1"]) & (
                            df_filtered[n]["HR[bpm]"].shift(1) <= df_filtered[n]["Seuil 1"])
                        if not df_filtered[n][cond].empty:
                            if debug:
                                print("threshold 1 found")
                            indexes = df_filtered[n][cond].index.tolist()
                            target_muscul = df_filtered[n].loc[indexes[0] -
                                                               5: indexes[0]+5]
                            if len(indexes) > 1:
                                if debug:
                                    print("several matches found")
                                # iterate over the matches found
                                for i in range(len(indexes)-1):
                                    target_muscul = pd.concat(
                                        [target_muscul, df_filtered[n].loc[indexes[i+1]-5: indexes[i+1]+5]])
                            # iterate over the muscle groups
                            for m in stored_data[value][1][0]:
                                threshold_muscul[0].append(
                                    target_muscul[m].mean())
                if seuils[value][1] > 0:
                    if debug:
                        print("compute the second threshod")
                    # iterate over the levels of the test
                    for n in range(len(df_filtered)):
                        cond = (df_filtered[n]["HR[bpm]"] > df_filtered[n]["Seuil 2"]) & (
                            df_filtered[n]["HR[bpm]"].shift(1) <= df_filtered[n]["Seuil 2"])
                        if not df_filtered[n][cond].empty:
                            if debug:
                                print("threshold 2 found")
                            indexes = df_filtered[n][cond].index.tolist()
                            target_muscul = df_filtered[n].loc[indexes[0] -
                                                               5: indexes[0]+5]
                            if len(indexes) > 1:
                                if debug:
                                    print("several matches found")
                                # iterate over the matches found
                                for i in range(len(indexes)-1):
                                    target_muscul = pd.concat(
                                        [target_muscul, df_filtered[n].loc[indexes[i+1]-5: indexes[i+1]+5]])
                            # iterate over the muscle groups
                            for m in stored_data[value][1][0]:
                                threshold_muscul[1].append(
                                    target_muscul[m].mean())
                print(threshold_muscul)
                analytics[1] = threshold_muscul

            # find min and max for each muscular groups
            df_filtered_concat = pd.concat(df_filtered)
            min_max = []
            for m in stored_data[value][1][0]:
                min_max.append(df_filtered_concat[m].min())
            print(min_max)
            analytics[0] = min_max

            print(analytics)
            return analytics
        else:
            return None

    @callback(
        Output("vo2-data", "data"),
        [Input("vo2-upload", "contents")],
        State("test-choice", 'value'),
        State("vo2-data", "data")
    )
    def store_xml(content, value, stored_content):
        if debug:
            print('--store_xml--')
        if content:
            content_type, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            [df, time] = read_xml.parse_xml(decoded)
            if stored_content:
                stored_content[value] = [df.to_json(), time]
                return stored_content
            else:
                return {value: [df.to_json(), time]}
        else:
            raise PreventUpdate
