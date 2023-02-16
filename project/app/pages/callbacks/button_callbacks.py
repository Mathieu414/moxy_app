from dash import Input, Output, State, callback, ClientsideFunction, clientside_callback
from dash.exceptions import PreventUpdate

from pages.utils.toPdf.toLatex import generateLatex


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

    """
    clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='printPdf'
        ),
        Output('print-pdf', 'disabled'),
        Input('print-pdf', 'n_clicks'),
        prevent_initial_call=True
    )
    """

    @callback(
        Output('print-pdf', 'disabled'),
        Input('print-pdf', 'n_clicks'),
        State('test-zoom-chart', 'figure'),
        State('div-table', "children"),
        prevent_initial_call=True)
    def print_to_pdf(n_clicks, zoom_fig, table):
        if debug:
            print("--print_to_pdf--")
        generateLatex(zoom_fig, table)
