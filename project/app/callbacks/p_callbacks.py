from dash_extensions.enrich import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate


def get_p_callbacks(page, debug=True):
    @page.callback(
        [Output("vo2_p", "children"), Output("vo2_p", "className")],
        Input("test-choice", "value"),
        State("raw-data", "data"),
    )
    def update_p(value, data):
        if debug:
            print("--update_p--")
        if value is not None and data is not None:
            print
            return ["3. Importer les données VO2 du test", ""]
        else:
            return ["3.Choisir un test avant de charger le fichier VO2", "error"]

    @page.callback(
        Output("error-p-full-graph", "children"),
        Output("error-p-full-graph", "className"),
        Input("global-analysis-button", "n_clicks"),
        Input("local-analysis-button", "n_clicks"),
        Input("test-choice", "value"),
        State("test-chart", "selectedData"),
        State("selected-data", "data"),
        State("trend-data", "data"),
        prevent_initial_call=True,
    )
    def full_graph_error(
        n_clicks,
        n_clicks2,
        value,
        selected_data,
        stored_selected_data,
        stored_trend_data,
    ):
        if (
            ctx.triggered_id == "global-analysis-button"
            and selected_data is None
            and (stored_selected_data is None or value not in stored_selected_data)
        ) or (
            ctx.triggered_id == "local-analysis-button"
            and selected_data is None
            and (stored_trend_data is None or value not in stored_trend_data)
        ):
            return ["Aucune donnée selectionnée", "error"]
        else:
            return ["", ""]
