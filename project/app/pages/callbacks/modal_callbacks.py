from dash_extensions.enrich import Input, Output, State, callback, html, dcc
from dash.exceptions import PreventUpdate


def get_modal_callbacks(page, debug=True):
    @page.callback(
        Output("modal", "open"),
        [Input("modal_open", "n_clicks"), Input("modal_close",
                                                "n_clicks"), Input("modal_abort", "n_clicks")],
        [State("modal", "open")],
    )
    def toggle_modal(n1, n2, n3, open):
        if n1 or n2 or n3:
            return not open
        return open

    @page.callback(
        Output("modal_content", "children"),
        [Input("data-upload", "data"), Input("test-choice", 'value')],
    )
    def set_modal_content(data, value):
        content = []
        if (data is not None) and (value is not None):
            for i, n in enumerate(data[value][1][0]):
                content.append(
                    html.Label(
                        [("Moxy n° " + data[value][1][1][i]), dcc.Input(id={'type': 'muscle-input', 'index': str(i)}, name=("moxy" + data[value][1][1][i]), type='text', value=n, debounce=True)], style={"margin-left": "15%", "margin-right": "15%"}))
            return content
