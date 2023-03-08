from pages.utils.toPdf.toLatex import generateLatex
from dash import Input, Output, State, callback, ClientsideFunction, clientside_callback
from dash.exceptions import PreventUpdate
import time


def get_button_callbacks(debug=True):
    @callback([Output('vo2_button', 'disabled'),
              Output('vo2_button', 'className')],
              Input("test-choice", 'value')
              )
    def set_button_enabled_state(value):
        if value is not None:
            return [False, ""]
        else:
            return [True, "secondary outline"]

    @callback([Output('modal_open', 'disabled'),
              Output('modal_open', 'className')],
              Input("test-choice", 'value')
              )
    def set_button_enabled_state(value):
        if value is not None:
            return [False, ""]
        else:
            return [True, "secondary outline"]

    @callback(
        Output('render', 'n_clicks'),
        Input('div-hr', 'children'),
        State('print-pdf', 'n_clicks'),
        prevent_initial_call=True
    )
    def print_func(children, n_clicks):
        print("NOMBRE DE CLICKS : " + str(n_clicks))
        if n_clicks is not None:
            if n_clicks > 0:
                return 0
            else:
                raise PreventUpdate
        else:
            raise PreventUpdate

    clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='printPdf'
        ),
        Output('analytics', 'storage_type'),
        Input('render', 'n_clicks'),
        prevent_initial_call=True
    )

    clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='changeVariable'
        ),
        Output('test-zoom-chart', 'style'),
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
    """
