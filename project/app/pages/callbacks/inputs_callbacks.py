from dash_extensions.enrich import Input, Output, State, callback
import pandas as pd


def get_threshold_callbacks(page, debug=True):
    @ page.callback(
        [Output('seuil1-p', 'value'),
         Output('seuil2-p', 'value'),
         Output('seuil1', 'disabled'),
         Output('seuil2', 'disabled'),
         Output('seuil1', 'value'),
         Output('seuil2', 'value')],
        Input('test-choice', 'value'),
        State('seuils', 'data'),
        State("data-upload", 'data'),
        prevent_initial_call=True
    )
    def check_thresholds(value, seuils, data):
        if debug:
            print("--check_thresholds--")
            print(seuils)
        if (data is not None) and (value is not None) and ("HR[bpm]" in data[value][0].columns):
            seuils = seuils[value]
            if debug:
                print("threshold enabled")
            value_seuil1 = seuils[0]
            value_seuil2 = seuils[1]
            return [value_seuil1, value_seuil2, False, False, value_seuil1, value_seuil2]
        else:
            if debug:
                print("seuils or value is None")
            return [None, None, True, True, None, None]

    @page.callback([Output('prominence', 'value'),
                    Output('width', 'value'),
                    Output('removed_width_left', 'value'),
                    Output('removed_width_right', 'value')],
                   Input('test-choice', 'value'),
                   State('peaks-parameters', 'data')
                   )
    def set_value_detection_input(value, data):
        if debug:
            print("--set_value_detection_input--")
            print("valeur du seuil de detection")
            print(data)
        if (data is not None) and (value is not None):
            return data[value]
        else:
            return [None, None, None, None]
