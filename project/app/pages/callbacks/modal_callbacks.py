from dash import Input, Output, State, callback, no_update, html, dcc
from dash.exceptions import PreventUpdate


def get_modal_callbacks(debug=True):
    @callback(
        Output("modal", "open"),
        [Input("modal_open", "n_clicks"), Input("modal_close", "n_clicks")],
        [State("modal", "open")],
    )
    def toggle_modal(n1, n2, open):
        if n1 or n2:
            return not open
        return open

    @callback(
        Output("modal_content", "children"),
        [Input("data-upload", "data"), Input("test-choice", 'value')],
    )
    def set_modal_content(data, value):
        content = []
        if (data is not None) and (value is not None):
            for i, n in enumerate(data[value][1][0]):
                content.append(html.Div([
                    html.P("Groupe musculaire " + str(i+1)),
                    dcc.Input(id={'type': 'muscle-input', 'index': str(i)}, type='text', value=n)], className="grid"))
            return content
