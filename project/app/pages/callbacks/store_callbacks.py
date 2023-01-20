from dash import Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from scipy import signal
import pages.utils.functions as fc


def get_store_callbacks(debug=True):
    @callback(
        [Output('data-upload', 'data'),
         Output('seuils', 'data')],
        [Input("test-upload", "contents"),
         Input("test-upload", "filename"),
         Input("seuil1", 'value'),
         Input("seuil2", 'value'),
         Input("clear-button", "n_clicks"),
         Input("test-choice", 'value'),
         Input("test-chart", "selectedData"),
         Input("filter-selection-button", "n_clicks")],
        [State("data-upload", 'data'),
         State("seuils", "data")],
        prevent_initial_call=True,
    )
    def data_upload(contents, filenames, seuil1, seuil2, clear_button, value, selectedData, filter_button, stored_data, stored_seuils):
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

            new_seuils = [None, None]

            if "HR[bpm]" in data[0].columns:
                data[0]["HR[bpm]"] = signal.savgol_filter(
                    data[0]["HR[bpm]"], 40, 4)
                new_seuils = [0, 0]

            data[0] = data[0].to_json()
            if stored_data:
                stored_data.append([data[0], data[1]])
                return [stored_data, stored_seuils.append(new_seuils)]
            else:
                return [[[data[0], data[1]]], [new_seuils]]
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
                df_filtered = pd.read_json(stored_data[value][3])
            if (seuil1 is not None) and (seuil1 != 0):
                df["Seuil 1"] = seuil1
                if df_selected is not None:
                    df_selected["Seuil 1"] = seuil1
                if df_filtered is not None:
                    df_filtered["Seuil 1"] = seuil1
            if (seuil2 is not None) and (seuil2 != 0):
                if debug:
                    print("seuil2 is not None and not 0")
                df["Seuil 2"] = seuil2
                if df_selected is not None:
                    df_selected["Seuil 2"] = seuil2
                if df_filtered is not None:
                    df_filtered["Seuil 2"] = seuil2
            df = df.to_json()
            stored_data[value][0] = df
            if df_selected is not None:
                df_selected = df_selected.to_json()
                stored_data[value][2] = df_selected
            if df_filtered is not None:
                df_filtered = df_filtered.to_json()
                stored_data[value][3] = df_filtered
            stored_seuils[value] = [seuil1, seuil2]
            return [stored_data, stored_seuils]
        if (ctx.triggered_id == "clear-button") and (clear_button > 0):
            if debug:
                print("Clearing data")
            stored_data = None
            return [stored_data, no_update]
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
                df = pd.DataFrame()
                df["Slope"] = fc.df_slope(data_selected["HR[bpm]"])
                data_selected = data_selected.join(df)
                print(data_selected)
                if len(stored_data[value]) >= 3:
                    stored_data[value][2] = data_selected.to_json()
                else:
                    stored_data[value].append(data_selected.to_json())
                return [stored_data, no_update]
        if (ctx.triggered_id == "filter-selection-button"):
            if debug:
                print("--filter_selection--")
            if len(stored_data[value]) >= 3:
                data_selected = pd.read_json(stored_data[value][2])
                data_selected = fc.cut_pauses(data_selected)
                data_selected = fc.cut_begining_end(data_selected)

                if len(stored_data[value]) >= 4:
                    stored_data[value][3] = data_selected.to_json()
                else:
                    stored_data[value].append(data_selected.to_json())
                return [stored_data, no_update]
        else:
            if debug:
                print("prevent update data_upload")
            raise PreventUpdate
