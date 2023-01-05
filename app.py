import dash
from dash import html

app = dash.Dash(
    use_pages=True
)


def nav():
    nav = html.Nav(
        [
            html.Ul(
                html.Li([html.Strong("Moxy app")])
            ),
            html.Ul([
                html.Li(
                    [html.A('Séance',  href=dash.page_registry['pages.analyse_seance']['path'], role="button")]),
                html.Li(
                    [html.A('Test',  href=dash.page_registry['pages.analyse_test']['path'], role="button")])
            ])
        ]
    )
    return nav


app.layout = html.Main([nav(), dash.page_container], className="container")


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)