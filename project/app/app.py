from flask import Flask, redirect
import dash
from dash import html

server = Flask(__name__)


@server.route('/')
def index_redirect():
    return redirect('/analyse-test')


app = dash.Dash(
    __name__,
    server=server,
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


server = app.server
