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
        Output("trend-data-table", "data"),
        Input("trend-parameters", "data"),
        Input("test-choice", "value"),
        Input("analysis-type", "data"),
    )
    def set_trend_table(parameters, value, analysis_type):
        if debug:
            print("--set_trend_table--")
            print(parameters)
        if parameters is not None and str(value) in parameters:
            df = pd.DataFrame.from_dict(
                parameters[str(value)],
                orient="index",
                columns=["Moyenne (%)", "Pente (%/s)"],
            )
            df = df.round(3)
            df.reset_index(inplace=True, names=["Groupes musculaires"])
            print(df)
            return df.to_dict("records")
