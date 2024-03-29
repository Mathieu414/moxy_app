from dash_extensions.enrich import Input, Output, State, callback
from dash.exceptions import PreventUpdate


def get_dropdown_callbacks(page, debug=True):
    @page.callback(
        Output("test-choice", "options"),
        Input("raw-data", "data"),
        State("test-choice", "options"),
    )
    def dropdown_update(data, options):
        if debug:
            print("--dropdown_update--")
        if data is not None:
            if debug:
                print("longueur de la liste 'raw-data' : " + str(len(data)))
            new_options = [
                {"label": "Test n°" + str(session + 1), "value": session}
                for session in range(len(data))
            ]
            print(new_options)
            if options is not None:
                if len(options) != len(new_options):
                    return new_options
            if options is None:
                return new_options
            else:
                raise PreventUpdate
        if (data is None) and (options is not None):
            if debug:
                print("Data is None but options is not None")
            return {}
        else:
            raise PreventUpdate

    @page.callback(
        Output("test-choice", "value"),
        Input("clear-button", "n_clicks"),
    )
    def clear_value(clear_button):
        return None
