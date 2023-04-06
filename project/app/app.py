from flask import Flask, redirect
import dash_labs as dl
from dash_extensions.enrich import DashBlueprint, DashProxy, ServersideOutputTransform, html, Output, Input
import dash
import plotly.io as pio
from flask_caching import Cache
from pages.analyse_test import test_page
from pages.analyse_seance import seance_page

server = Flask(__name__)


@server.route('/')
def index_redirect():
    return redirect('/test')


pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"]['layout']['paper_bgcolor'] = '#141e26'
pio.templates["plotly_dark_custom"]['layout']['plot_bgcolor'] = '#141e26'
pio.templates["plotly_dark_custom"]['layout']['dragmode'] = 'select'

pio.templates.default = "plotly_dark_custom"

app = DashProxy(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    transforms=[ServersideOutputTransform()],
    use_pages=True
)


t_page = test_page()
s_page = seance_page()


s_page.register(app, "Seance")
t_page.register(app, "Test")


def nav():
    nav = html.Nav(
        [
            html.Ul(
                html.Li([html.Strong("Moxy app")])
            ),
            html.Ul([
                html.Li(
                    [html.A('Séance',  href=dash.page_registry['Seance']['path'], role="button")]),
                html.Li(
                    [html.A('Test',  href=dash.page_registry['Test']['path'], role="button")])
            ])
        ], className="no-print")
    return nav


app.layout = html.Main([nav(), dash.page_container],
                       className="container", id="container")


server = app.server

if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
