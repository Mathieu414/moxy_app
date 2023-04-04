from dash_extensions.enrich import Input, Output, State, callback
from dash.exceptions import PreventUpdate


def get_p_callbacks(page, debug=True):
    @page.callback(
        [Output("vo2_p", "children"),
         Output("vo2_p", "className")],
        Input("test-choice", 'value'),
        State('data-upload', 'data')
    )
    def update_p(value, data):
        if debug:
            print("--update_p--")
        if value is not None and data is not None:
            print
            return ["3. Importer les données VO2 du test", ""]
        else:
            return ["3.Choisir un test avant de charger le fichier VO2", "error"]
