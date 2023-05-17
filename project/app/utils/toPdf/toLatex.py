import numpy as np
import plotly.graph_objects as go

from pylatex.base_classes import Environment, SpecialOptions, Command, CommandBase
from pylatex.package import Package
from pylatex import (
    Document,
    Section,
    Subsection,
    Tabular,
    Math,
    TikZ,
    Axis,
    Plot,
    Figure,
    Matrix,
    Alignat,
    NoEscape,
    PageStyle,
    Head,
    MiniPage,
    StandAloneGraphic,
    LargeText,
    LineBreak,
    MediumText,
    Command,
    Foot,
    simple_page_number,
    MdFramed,
    UnsafeCommand,
    Tabu,
    SubFigure,
    NewLine,
)
from pylatex.utils import italic, bold, NoEscape, fix_filename
from pylatex.position import (
    VerticalSpace,
    HorizontalSpace,
    Center,
    FlushLeft,
    FlushRight,
)
import os
import shutil

mdframed_options = {
    "backgroundcolor": "mygray",
    "hidealllines": "true",
    "roundcorner": "10pt",
}


class DefineColor(UnsafeCommand):
    """Add/remove the amount of horizontal space between elements."""

    _latex_name = "definecolor"

    packages = [Package("xcolor", options="dvipsnames")]

    _repr_attributes_mapping = {
        "name": "arguments",
        "base_color": "arguments",
        "color": "arguments",
    }

    def __init__(self, name, base_color, color):
        arguments = [name, base_color, color]
        super().__init__(arguments=arguments)


def generateLatex(filtered_fig, vo2_fig, hr_div, reference_data, first_name, last_name):
    print("--generateLatex--")

    filtered_fig = go.Figure(filtered_fig)
    vo2_fig = go.Figure(vo2_fig)

    hr_filenames = []

    if not os.path.exists("export"):
        os.mkdir("export")
    if os.path.exists("export/images"):
        print("remove folder")
        shutil.rmtree("export/images", ignore_errors=False, onerror=None)
    os.mkdir("export/images")
    export_path = os.path.abspath("export/images")
    print("writing image")
    filtered_fig.write_image("export/images/filtered_fig.jpg", width=800, height=500)
    print("filtered image exported !")
    vo2_fig.write_image("export/images/vo2_fig.jpg", width=800, height=500)
    print("vo2 image exported !")

    # get the graph nested inside the upper Article and Div
    if hr_div is not None:
        hr_graphs = hr_div["props"]["children"][1]["props"]["children"]
        for i, v in enumerate(hr_graphs):
            v = v["props"]["children"][1]
            hr_filenames.append("export/images/hr_graph_" + str(i) + ".jpg")
            go.Figure(v["props"]["figure"]).write_image(
                hr_filenames[-1], width=800, height=500
            )
        print("hr images exported !")

    filtered_fig_filename = os.path.join(export_path, "filtered_fig.jpg")
    vo2_fig_filename = os.path.join(export_path, "vo2_fig.jpg")
    for v in hr_filenames:
        v = os.path.join(export_path, v)

    assets_folder = os.path.join(os.path.dirname(__file__), "..\..\\assets\\")

    geometry_options = {
        "head": "60pt",
        "margin": "0.5in",
        "bottom": "0.6in",
        "includeheadfoot": True,
    }
    doc = Document(geometry_options=geometry_options)
    doc.packages.append(Package("xcolor", options="dvipsnames"))
    doc.packages.append(Package("lexend"))
    doc.packages.append(Package("mdframed", options="framemethod=TikZ"))
    doc.append(DefineColor("mygray", "gray", "0.85"))
    # Add document header
    header = PageStyle("header")
    # Create left header
    with header.create(Head("R")) as right_header:
        with right_header.create(
            MiniPage(width=NoEscape(r"0.49\textwidth"), pos="c", align="r")
        ) as logo_wrapper:
            logo_file = fix_filename(
                os.path.join(os.path.dirname(__file__), "logo.png")
            )
            logo_wrapper.append(
                StandAloneGraphic(image_options="width=120px", filename=logo_file)
            )
    # Create right header
    with header.create(Head("L")) as left_header:
        with left_header.create(
            MiniPage(width=NoEscape(r"0.49\textwidth"), pos="c", align="l")
        ) as title_wrapper:
            title_wrapper.append(LargeText("RAPPORT DE TEST PHYSIOLOGIQUE"))
    # Create left footer
    with header.create(Foot("L")):
        header.append("CNSNMM")
    # Create right footer
    with header.create(Foot("R")):
        header.append(Command("date", NoEscape(r"\today")))

    doc.preamble.append(header)
    doc.change_document_style("header")

    with doc.create(Tabu("X[c]")) as table_0:
        infos = MiniPage(width=NoEscape(r"0.95\textwidth"))
        frame = MdFramed(options=mdframed_options)
        frame.append(VerticalSpace("10pt"))
        center = Center()
        center.append(LargeText(last_name + "  "))
        center.append(MediumText(first_name))
        frame.append(center)
        frame.append(VerticalSpace("10pt"))
        infos.append(frame)

        table_0.add_row([infos])
        table_0.add_empty_row()

    if reference_data is not None:
        print(reference_data)
        with doc.create(Tabu("X[l] X[c] X[r]")) as table_1:
            # Add threshold 1 infos
            seuil_1 = create_data_table(reference_data, "Seuil1", "Seuil 1")

            # Add threshold 2 infos
            seuil_2 = create_data_table(reference_data, "Seuil2", "Seuil 2")

            # Add add val max/min infos
            max_min = create_data_table(
                reference_data, "Desoxygénation minimale", "Desoxygénation minimale"
            )
            table_1.add_row([seuil_1, seuil_2, max_min])

    with doc.create(Center()) as graph_title:
        graph_title.append(LargeText("Graphiques"))

    with doc.create(Tabu("X[l] X[r]")) as table_2:
        table_2.add_row(create_subfigures(filtered_fig_filename, vo2_fig_filename))

        if len(hr_filenames) > 1:
            table_2.add_row(
                create_subfigures(
                    hr_filenames[0], hr_filenames[1], im_size=r"width=0.6\textwidth"
                )
            )

        if len(hr_filenames) > 3:
            table_2.add_row(
                create_subfigures(
                    hr_filenames[2], hr_filenames[3], im_size=r"width=0.6\textwidth"
                )
            )

    doc.generate_pdf("Rapport", clean_tex=False, compiler="lualatex")


def create_data_table(reference_data, data_name, frame_name):
    mini_page = MiniPage(width=NoEscape(r"0.30\textwidth"), pos="t", height="130px")
    frame = MdFramed(options=mdframed_options)
    frame.append(VerticalSpace("10pt"))
    with frame.create(Center()) as title:
        title.append(LargeText(frame_name))
    frame.append(VerticalSpace("3pt"))
    table = Tabu("X[l] X[c] X[r]")
    names = MiniPage(width=NoEscape(r"0.45\textwidth"), pos="t!", align="l")
    rule = MiniPage(width=NoEscape(r"0.1\textwidth"), pos="t!", align="c")
    data = MiniPage(width=NoEscape(r"0.45\textwidth"), pos="t!", align="l!")
    if data_name in reference_data[0]:
        for d in reference_data:
            names.append(d["Groupes musculaires"])
            names.append(NewLine())
            data.append(str(d[data_name]))
            data.append(NewLine())
    rule.append(NoEscape(r"\noindent\rule[-1ex]{1pt}{15ex}"))
    table.add_row([names, rule, data])
    frame.append(table)
    frame.append(VerticalSpace("5pt"))
    mini_page.append(frame)

    return mini_page


def create_subfigures(left_fig, right_fig, im_size=r"width=\textwidth"):
    left_mini = MiniPage(width=NoEscape(r"0.50\textwidth"), align="c")
    left_mini.append(
        StandAloneGraphic(
            image_options=im_size,
            filename=fix_filename(left_fig),
        )
    )

    right_mini = MiniPage(width=NoEscape(r"0.50\textwidth"), align="c")
    right_mini.append(
        StandAloneGraphic(
            image_options=im_size,
            filename=fix_filename(right_fig),
        )
    )

    return [left_mini, right_mini]
