from dash import Input, Output, State, callback
import pandas as pd


def get_threshold_callbacks(debug=True):
    @ callback(
        [Output('seuil1', 'disabled'),
         Output('seuil2', 'disabled'),
         Output('seuil1', 'value'),
         Output('seuil2', 'value')],
        Input('test-choice', 'value'),
        State('data-upload', 'data'),
        prevent_initial_call=True
    )
    def check_thresholds(value, data):
        if debug:
            print("--check_thresholds--")
        if (data is not None) and (value is not None):
            if debug:
                print("dataset columns: ")
                print(pd.read_json(data[value][0]).columns)
                print("Test de 'value' :")
                print(value == False)
            data = data[value]
            data[0] = pd.read_json(data[0])
            if "HR[bpm]" in data[0].columns:
                if debug:
                    print("threshold enabled")
                value_seuil1 = None
                value_seuil2 = None
                if ("Seuil 1" in data[0].columns):
                    value_seuil1 = data[0]["Seuil 1"][0]
                    print(value_seuil1)
                if ("Seuil 2" in data[0].columns):
                    value_seuil2 = data[0]["Seuil 2"][0]
                    print(value_seuil2)
                return [False, False, value_seuil1, value_seuil2]
            else:
                if debug:
                    print("HR is not in data")
                return [True, True, None, None]
        else:
            if debug:
                print("data or value is None")
            return [True, True, None, None]
