from dash_extensions.enrich import (
    Input,
    Output,
    State,
    callback,
    html,
    dcc,
    clientside_callback,
    ClientsideFunction,
)
from dash.exceptions import PreventUpdate


def get_modal_callbacks(page, debug=True):
    @page.callback(
        Output("modal", "open"),
        [
            Input("modal_open", "n_clicks"),
            Input("modal_close", "n_clicks"),
            Input("modal_abort", "n_clicks"),
        ],
        [State("modal", "open")],
    )
    def toggle_modal(n1, n2, n3, open):
        if n1 or n2 or n3:
            return not open
        return open

    @page.callback(
        Output("modal_content", "children"),
        [Input("raw-data", "data"), Input("test-choice", "value")],
        [State("muscle-groups", "data")],
    )
    def set_modal_content(data, value, muscle_groups):
        content = []
        if (data is not None) and (value is not None):
            for i, n in enumerate(list(muscle_groups[value][0].keys())):
                content.append(
                    html.Label(
                        [
                            ("Moxy n° " + muscle_groups[value][1][i]),
                            dcc.Input(
                                id={"type": "muscle-input", "index": str(i)},
                                name=("moxy" + muscle_groups[value][1][i]),
                                type="text",
                                value=n,
                                debounce=True,
                            ),
                        ],
                        style={"marginLeft": "15%", "marginRight": "15%"},
                    )
                )
            return content

    @page.callback(
        Output("modal-print", "open"),
        [
            Input("print-pdf", "n_clicks"),
            Input("modal-print-abort", "n_clicks"),
        ],
        [State("modal-print", "open")],
        prevent_initial_call=True,
    )
    def toggle_modal_print(n1, n2, open):
        if n1 or n2:
            return not open
        return open

    clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="set_loading"),
        Output("modal-print-content", "n_clicks"),
        Input("print-pdf", "n_clicks"),
    )

    clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="unset_loading"),
        Output("modal-print-content", "style"),
        Input("vo2-chart", "figure"),
    )
