from flask import Flask, redirect
import dash_labs as dl
from dash_extensions.enrich import (
    DashBlueprint,
    DashProxy,
    ServersideOutputTransform,
    html,
    Output,
    Input,
)
from dash_iconify import DashIconify
import dash
import plotly.io as pio
from pages.test import test_page
from pages.training import seance_page

server = Flask(__name__)


@server.route("/")
def index_redirect():
    return redirect("/test")


pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]
pio.templates["plotly_dark_custom"]["layout"]["paper_bgcolor"] = "#181c25"
pio.templates["plotly_dark_custom"]["layout"]["plot_bgcolor"] = "#181c25"
pio.templates["plotly_dark_custom"]["layout"]["dragmode"] = "select"


app = DashProxy(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    transforms=[ServersideOutputTransform()],
    use_pages=True,
)


t_page = test_page()
s_page = seance_page()

s_page.register(app, "Seance")
t_page.register(app, "Test")


def nav():
    nav = html.Nav(
        [
            html.Ul(
                [
                    html.Li(
                        html.Img(
                            src="/assets/images/android-chrome-512x512.png",
                            style={"width": "3rem"},
                        ),
                    ),
                    html.Li(
                        [
                            html.Strong("Moxy app"),
                        ]
                    ),
                ]
            ),
            html.Ul(
                [
                    html.Li(
                        [
                            html.A(
                                "Test",
                                href=dash.page_registry["Test"]["path"],
                                role="button",
                            )
                        ]
                    ),
                    html.Li(
                        [
                            html.A(
                                "Séance",
                                href=dash.page_registry["Seance"]["path"],
                                role="button",
                            )
                        ]
                    ),
                ]
            ),
        ],
        className="no-print",
    )
    return nav


Footer = html.Footer(
    children=html.Small(
        children=[
            DashIconify(icon="uil:copyright"),
            html.A("CNSNMM", href="https://cnsnmm.sports.gouv.fr/", target="_blank"),
            " • ",
            html.A(
                "Source code",
                href="https://github.com/Mathieu414/moxy_app",
                target="_blank",
            ),
        ]
    )
)


app.layout = html.Main(
    [nav(), dash.page_container, Footer], className="container", id="container"
)


server = app.server

if __name__ == "__main__":
    app.run_server(port=8050, debug=True, host="0.0.0.0")
