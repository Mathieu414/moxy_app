from flask import Flask, redirect
import dash
from dash import html
import darkdetect
import plotly.io as pio

server = Flask(__name__)


@server.route('/')
def index_redirect():
    return redirect('/analyse-test')


pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"]['layout']['paper_bgcolor'] = '#141e26'
pio.templates["plotly_dark_custom"]['layout']['plot_bgcolor'] = '#141e26'
pio.templates["plotly_dark_custom"]['layout']['dragmode'] = 'select'

pio.templates.default = "plotly_dark_custom"

print()


app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True
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
        ], className="no-print")
    return nav


app.layout = html.Main([nav(), dash.page_container],
                       className="container", id="container")


server = app.server

if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
