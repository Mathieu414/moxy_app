from dash import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from scipy import signal
import pages.utils.functions as fc


def get_store_callbacks(debug=True):
    @callback(
        Output('data-upload', 'data'),
        [Input("test-upload", "contents"),
         Input("test-upload", "filename"),
         Input("seuil1", 'value'),
         Input("seuil2", 'value'),
         Input("clear-button", "n_clicks")],
        [State("data-upload", 'data'),
         State("test-choice", 'value')],
        prevent_initial_call=True,
    )
    def data_upload(contents, filenames, seuil1, seuil2, n_clicks, stored_data, value):
        if debug:
            print("--data-upload--")
        if (ctx.triggered_id == "test-upload") and ('Details.txt' in filenames):
            t_id = filenames.index('Details.txt')
            x_id = filenames.index('DataAverage.xlsx')
            data = []
            for content, filename in zip(contents, filenames):
                data.append(fc.parse_data(content, filename))

            smo_cols = [col for col in data[x_id].columns if 'SmO2' in col]

            col_names = dict(zip(smo_cols, data[t_id]))

            data[x_id].rename(columns=col_names, inplace=True)

            # check if the elements are in the right order
            if t_id == 0:
                data[0], data[1] = data[1], data[0]
            data[0].replace(0, np.nan, inplace=True)

            # smooth the data
            for n in data[1]:
                data[0][n] = signal.savgol_filter(data[0][n], 40, 3)

            if "HR[bpm]" in data[0].columns:
                data[0]["HR[bpm]"] = signal.savgol_filter(
                    data[0]["HR[bpm]"], 40, 4)

            data[0] = data[0].to_json()
            if stored_data:
                stored_data.append([data[0], data[1]])
                return stored_data
            else:
                return [[data[0], data[1]]]
        if debug:
            print("valeur de seuil1")
            print(seuil1)
            print("valeur de seuil2")
            print(seuil2)
        if (ctx.triggered_id in ["seuil1", "seuil2"]) and (not all(s is None for s in (seuil1, seuil2))):
            if debug:
                print("Seuil 1 or Seuil 2 are trigered and are not None")
            df = pd.read_json(stored_data[value][0])
            if seuil1 is not None:
                df["Seuil 1"] = seuil1
            if seuil2 is not None:
                df["Seuil 2"] = seuil2
            df = df.to_json()
            stored_data[value][0] = df
            return stored_data
        if (ctx.triggered_id == "clear-button") and (n_clicks > 0):
            if debug:
                print("Clearing data")
            stored_data = None
            return stored_data
        else:
            if debug:
                print("prevent update data_upload")
            raise PreventUpdate

    @ callback(
        Output("data-selection", "data"),
        [Input("test-chart", "selectedData"),
         Input('test-choice', 'value')],
        State('data-upload', 'data'),
        prevent_initial_call=True)
    def store_filtered_data(selectedData, value, data):
        if debug:
            print("--store_filtered_data--")
        if ctx.triggered_id == "test-chart":
            if debug:
                print("Creating data selection chart")
            data = data[value]
            data[0] = pd.read_json(data[0])
            selected_time = []
            if selectedData and selectedData['points']:
                for point in selectedData["points"]:
                    selected_time.append(point['x'])
                data[0] = data[0].query("`Time[s]` == @selected_time")
                df = pd.DataFrame()
                df["Slope"] = fc.df_slope(data[0]["HR[bpm]"])
                data[0] = data[0].join(df)
                print(data[0])
                data[0] = data[0].to_json()
                return data
        # if ctx.triggered_id == "test-choice":
            # if debug:
                # print("erasing data-selection")
            # return {}
        else:
            raise PreventUpdate
