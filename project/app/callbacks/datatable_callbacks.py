from dash_extensions.enrich import (
    Input,
    Output,
    State,
    callback,
    dcc,
    ctx,
    no_update,
)
from dash.exceptions import PreventUpdate
import pandas as pd


def get_datatable_callbacks(page, debug=True):
    @page.callback(
        [Output("trend-data-table", "data"), Output("trend-data-table", "columns")],
        Input("trend-parameters", "data"),
        Input("test-choice", "value"),
        Input("analysis-type", "data"),
    )
    def set_trend_table(parameters, value, analysis_type):
        if debug:
            print("--set_trend_table--")
            print(parameters)
        if parameters is not None and value in parameters:
            df = parameters[value]
            df = df.round(3)
            df.reset_index(inplace=True, names="")
            cols, data = convert_df_to_dash(df)
            return [data, cols]
        else:
            return [None, None]


def convert_df_to_dash(df):
    """
    Converts a pandas data frame to a format accepted by dash
    Returns columns and data in the format dash requires
    """

    # create ids for multi indexes (single index stays unchanged)
    # [('', 'A'), ('B', 'C'), ('D', 'E')] -> ['A', 'B_C', 'D_E']
    ids = ["".join([col for col in multi_col if col]) for multi_col in list(df.columns)]

    # build columns list from ids and columns of the dataframe
    cols = [{"name": list(col), "id": id_} for col, id_ in zip(list(df.columns), ids)]

    # build data list from ids and rows of the dataframe
    data = [{k: v for k, v in zip(ids, row)} for row in df.values]

    return cols, data
