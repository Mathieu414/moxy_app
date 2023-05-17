from utils.toPdf.toLatex import generateLatex
from dash_extensions.enrich import (
    Input,
    Output,
    State,
    callback,
    ClientsideFunction,
    clientside_callback,
    dcc,
    ctx,
)
from dash.exceptions import PreventUpdate
import dash
import time
import pdfkit


def get_button_callbacks(page, debug=True):
    @page.callback(
        [Output("vo2_button", "disabled"), Output("vo2_button", "className")],
        Input("test-choice", "value"),
    )
    def set_button_enabled_state(value):
        if value is not None:
            return [False, ""]
        else:
            return [True, "secondary outline"]

    @page.callback(
        [Output("modal_open", "disabled"), Output("modal_open", "className")],
        Input("test-choice", "value"),
    )
    def set_button_enabled_state(value):
        if value is not None:
            return [False, ""]
        else:
            return [True, "secondary outline"]

    @page.callback(
        Output("btn-download-pdf", "className"),
        Output("modal-print-validate", "children"),
        Input("modal-print-validate", "n_clicks"),
        State("test-filter-chart", "figure"),
        State("vo2-chart", "figure"),
        State("div-hr", "children"),
        State("div-table", "children"),
        State("report-first-name", "value"),
        State("report-last-name", "value"),
        prevent_initial_call=True,
    )
    def print_to_pdf(
        n_clicks, filtered_fig, vo2_fig, hr_div, table_div, first_name, last_name
    ):
        if debug:
            print("--print_to_pdf--")
        reference_table_data = None
        if table_div is not None:
            reference_table_data = table_div["props"]["children"][1]["props"]["data"]
        # muscle_zones_table_data = table_div["props"]["children"][3]["props"]['data']
        generateLatex(
            filtered_fig, vo2_fig, hr_div, reference_table_data, first_name, last_name
        )
        print("PDF generated !")
        return "", "Générer de nouveau"

    @page.callback(
        Output("download-pdf-file", "data"),
        Input("btn-download-pdf", "n_clicks"),
        prevent_initial_call=True,
    )
    def dowload_pdf(n_clicks):
        return dcc.send_file("Rapport.pdf")

    @page.callback(
        Output("refresh", "pathname"),
        Input("modal-print", "open"),
        prevent_initial_call=True,
    )
    def refresh(open):
        if ctx.triggered_id == "modal-print" and open == False:
            print("refresh")
            return "/"
