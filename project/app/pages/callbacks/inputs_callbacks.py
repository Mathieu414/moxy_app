from dash import Input, Output, State, callback
import pandas as pd


def get_threshold_callbacks(debug=True):
    @ callback(
        [Output('seuil1', 'disabled'),
         Output('seuil2', 'disabled'),
         Output('seuil1', 'value'),
         Output('seuil2', 'value')],
        Input('test-choice', 'value'),
        State('seuils', 'data'),
        prevent_initial_call=True
    )
    def check_thresholds(value, seuils):
        if debug:
            print("--check_thresholds--")
        if (seuils is not None) and (value is not None):
            seuils = seuils[value]
            if (seuils[0] is not None) or (seuils[1] is not None):
                if debug:
                    print("threshold enabled")
                value_seuil1 = seuils[0]
                value_seuil2 = seuils[1]
                return [False, False, value_seuil1, value_seuil2]
            else:
                if debug:
                    print("seuils are both None")
                return [True, True, None, None]
        else:
            if debug:
                print("seuils or value is None")
            return [True, True, None, None]
