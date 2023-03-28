from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate


def get_dropdown_callbacks(debug=True):
    @ callback(
        Output('test-choice', 'options'),
        Input('data-upload', 'data'),
        State('test-choice', 'options')
    )
    def dropdown_update(data, options):
        if debug:
            print("--dropdown_update--")
        if data:
            if debug:
                print("longueur de la liste 'data' : " + str(len(data)))
            new_options = [{"label": "Test n°" + str(session+1), "value": session}
                           for session in range(len(data))]
            if (options is not None):
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

    @ callback(
        Output('test-choice', 'value'),
        Input("clear-button", "n_clicks"),
    )
    def clear_value(clear_button):
        return None
