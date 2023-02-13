from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate


def get_button_callbacks(debug=True):
    @callback([Output('vo2_button', 'disabled'),
              Output('vo2_button', 'className')],
              Input("test-choice", 'value')
              )
    def set_button_enabled_state(value):
        if value is not None:
            return [False, ""]
        else:
            raise PreventUpdate
