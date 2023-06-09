from dash_extensions.enrich import Input, Output, State, callback
import pandas as pd


def get_threshold_callbacks(page, debug=True):
    @page.callback(
        [
            Output("threshold1-p", "value"),
            Output("threshold2-p", "value"),
            Output("threshold1", "disabled"),
            Output("threshold2", "disabled"),
            Output("threshold1", "value"),
            Output("threshold2", "value"),
        ],
        Input("test-choice", "value"),
        State("thresholds", "data"),
        State("raw-data", "data"),
        prevent_initial_call=True,
    )
    def check_thresholds(value, thresholds, data):
        if debug:
            print("--check_thresholds--")
            print(thresholds)
        if (
            (data is not None)
            and (value is not None)
            and ("HR[bpm]" in data[value].columns)
        ):
            thresholds = thresholds[value]
            if debug:
                print("threshold enabled")
            value_threshold1 = thresholds[0]
            value_threshold2 = thresholds[1]
            return [
                value_threshold1,
                value_threshold2,
                False,
                False,
                value_threshold1,
                value_threshold2,
            ]
        else:
            if debug:
                print("thresholds or value is None")
            return [None, None, True, True, None, None]

    @page.callback(
        [
            Output("prominence", "value"),
            Output("width", "value"),
            Output("removed_width_left", "value"),
            Output("removed_width_right", "value"),
        ],
        Input("test-choice", "value"),
        State("peaks-parameters", "data"),
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
