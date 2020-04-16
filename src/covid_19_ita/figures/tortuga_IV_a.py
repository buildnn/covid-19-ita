from os.path import join

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from covid_19_ita import SITE_DIR
from covid_19_ita.figures.tortuga_IV import (
    get_bilancio_datasets,
    get_covid_datasets,
    p2,
    plot,
    programmi,
)
from covid_19_ita.utils import watermark

pd.options.display.max_rows = 6

EXPORT_DIR = join(SITE_DIR, "figures", "tortuga", "IV")
config = {
    "Zoom": True,
    "displaylogo": False,
}
labels = {
    "tot_n_tests": "N. Test Effettuati",
    "tot_n_tests_pthab": "N. Test Effettuati per 1000 abitanti",
    "time": "Data",
    "active_cases": "Casi Attivi",
    "epidemic_age": "Giorni Trascorsi dal 100° Contagio",
    "n_deceased": "Decessi",
}


if __name__ == "__main__":

    covid, tests = get_covid_datasets()

    fig_a001 = plot(
        tests,
        x="time",
        y="tot_n_tests",
        pl_kwargs={
            "range_x": (tests.time.min(), tests.time.max() + pd.to_timedelta(36, "d"),)
        },
        labels=labels,
        title="<b>Test COVID effettuati per Nazione</b>",
        update_layout_kwargs={},
        line_shape=None,
    )
    fig_a001.update_layout(
        annotations=[
            dict(
                text="Fonte: Fonte: European Centre for Disease Prevention and Control, Our World in Data",
                showarrow=False,
                yref="paper",
                y=-240 / fig_a001.layout["height"],
                font={"color": "grey", "size": 9},
            )
        ],
    )
    fig_a001.show(config=config)
    fig_a001.write_html(
        join(EXPORT_DIR, "fig_a001.html"), include_plotlyjs="cdn", config=config,
    )

    # COVID per nazione
    fig_a002 = plot(
        tests.query("epidemic_age >= 0"),
        x="epidemic_age",
        y="tot_n_tests",
        pl_kwargs={"range_x": (0, 58)},
        labels=labels,
        title="<b>Test COVID effettuati per Nazione</b>",
        update_layout_kwargs={},
        line_shape=None,
    )
    fig_a002.update_layout(
        annotations=[
            dict(
                text="Fonte: Fonte: European Centre for Disease Prevention and Control, Our World in Data",
                showarrow=False,
                yref="paper",
                y=-240 / fig_a002.layout["height"],
                font={"color": "grey", "size": 9},
            )
        ],
    )
    fig_a002.show(config=config)
    fig_a002.write_html(
        join(EXPORT_DIR, "fig_a002.html"), include_plotlyjs="cdn", config=config,
    )

    # COVID per nazione
    fig_a003 = plot(
        tests.query("epidemic_age >= 0"),
        x="epidemic_age",
        y="tot_n_tests_pthab",
        pl_kwargs={"range_x": (0, 63)},
        labels=labels,
        title="<b>Test COVID effettuati per Nazione</b>",
        update_layout_kwargs={},
        line_shape=None,
    )
    fig_a003.update_layout(
        annotations=[
            dict(
                text="Fonte: Fonte: European Centre for Disease Prevention and Control, Our World in Data",
                showarrow=False,
                yref="paper",
                y=-240 / fig_a003.layout["height"],
                font={"color": "grey", "size": 9},
            )
        ],
    )
    fig_a003.show(config=config)
    fig_a003.write_html(
        join(EXPORT_DIR, "fig_a003.html"), include_plotlyjs="cdn", config=config,
    )

    df = covid[
        covid.geo.isin(
            list(covid.groupby("geo").active_cases.max().nlargest(9).index)
            + ["South_Korea"]
        )
    ]
    df = df.sort_values(["time", "geo"])
    df["geo"] = df["geo"].str.replace("_", " ")

    fig_a004 = plot(
        df,
        x="time",
        y="active_cases",
        pl_kwargs={"range_x": (pd.to_datetime("20200310"), pd.to_datetime("20200419"))},
        labels=labels,
        title="<b>Test COVID effettuati per Nazione</b>",
        update_layout_kwargs={"width": 500, "showlegend": True},
    )
    fig_a004.update_layout(
        annotations=[
            dict(
                text="Fonte: Fonte: European Centre for Disease Prevention and Control, Our World in Data",
                showarrow=False,
                yref="paper",
                y=-270 / fig_a004.layout["height"],
                font={"color": "grey", "size": 9},
            )
        ],
    )
    fig_a004.show(config={"displaylogo": False})
    fig_a004.write_html(
        join(EXPORT_DIR, "fig_a004.html"), include_plotlyjs="cdn", config=config,
    )

    df = covid[
        covid.geo.isin(
            list(covid.groupby("geo").active_cases.max().nlargest(9).index)
            + ["South_Korea"]
        )
    ]
    df = df.sort_values(["time", "geo"])
    df["geo"] = df["geo"].str.replace("_", " ")
    x = "time"
    y = "n_deceased"
    range_x = (0, 4600)
    labels = {
        "time": "Data",
        "epidemic_age": "Giorni Trascorsi dal 100° Contagio",
    }
    title = "<b>Test COVID effettuati per Nazione</b>"

    fig = plot(
        df,
        x,
        y,
        {"range_x": (pd.to_datetime("20200310"), pd.to_datetime("20200419"))},
        labels,
        title,
        {"width": 500, "showlegend": True},
    )
    fig.update_layout(
        annotations=[
            dict(
                text="Fonte: Fonte: European Centre for Disease Prevention and Control, Our World in Data",
                showarrow=False,
                yref="paper",
                y=-270 / fig.layout["height"],
                font={"color": "grey", "size": 9},
            )
        ],
    ).show(config={"displaylogo": False})

    df = covid[
        covid.geo.isin(
            list(covid.groupby("geo").active_cases.max().nlargest(9).index)
            + ["South_Korea"]
        )
    ]
    df = df.sort_values(["time", "geo"])
    df["geo"] = df["geo"].str.replace("_", " ")
    x = "time"
    y = "n_deceased"
    range_x = (0, 4600)
    labels = {
        "n_deceased": "Decessi",
        "time": "Data",
        "epidemic_age": "Giorni Trascorsi dal 100° Contagio",
    }
    title = "<b>Test COVID effettuati per Nazione</b>"

    fig = plot(
        df,
        x,
        y,
        {"range_x": (pd.to_datetime("20200310"), pd.to_datetime("20200419"))},
        labels,
        title,
        {"width": 500, "showlegend": True},
    )
    fig.update_layout(
        annotations=[
            dict(
                text="Fonte: Fonte: European Centre for Disease Prevention and Control, Our World in Data",
                showarrow=False,
                yref="paper",
                y=-270 / fig.layout["height"],
                font={"color": "grey", "size": 9},
            )
        ],
    ).show(config={"displaylogo": False})

    bilancio, bilancio_data = get_bilancio_datasets()

    (
        bilancio_data.style.format({"Previsioni iniziali competenza": "€ {0:,.0f}"})
        .bar(
            color="#FFA07A",
            vmin=10_000,
            subset=["Previsioni iniziali competenza"],
            align="zero",
        )
        .set_table_styles(
            [
                dict(selector="th", props=[("font-size", "100%"), ("height", "26px")],),
                dict(
                    selector="caption",
                    props=[
                        ("caption-side", "bottom"),
                        ("align", "left"),
                        ("margin-top", "25px"),
                    ],
                ),
            ]
        )
        .set_caption("Fonte: Open Data Ministero dell'Economia e Finanze.")
    )
    #
    for (h, mb), ammne in zip(
        [(650, -0.36), (750, -0.24)], bilancio["Descrizione Amministrazione"].unique(),
    ):
        subset = bilancio.loc[
            (bilancio["Descrizione Amministrazione"] == ammne)
            & bilancio["Descrizione Programma"].isin(programmi + p2)
        ]
        subset["Denominazione Capitolo"] = subset[
            "Denominazione Capitolo"
        ].str.capitalize()
        # desc_prog_short =
        f = px.bar(
            subset,
            x="Previsioni iniziali competenza",
            y=subset["Descrizione Programma"].apply(
                lambda x: x[:40] + "..." if len(x) >= 40 else x.rjust(50)
            ),
            color="Descrizione Azione",
            hover_data=["Denominazione Capitolo"],
            orientation="h",
            range_x=(0, 2.1e9),
        ).update_layout(
            title={
                "text": "<br><b>Previsioni iniziali competenza</b></br>"
                '<span style="font-size: 12;">{}'.format(ammne.title())
                + ": Dettaglio per Azione e Capitolo</span>",
                "x": 0.5,
            },
            showlegend=True,
            height=h,
            width=800,
            margin={"b": 280, "l": 240, "t": 180, "autoexpand": False},
            legend={
                "orientation": "h",
                "x": 0.0,
                "y": mb,
                "xanchor": "left",
                "yanchor": "top",
                "title": None,
            },
            yaxis={"title": None},
            annotations=[
                dict(
                    text="Fonte: Fonte: Open Data Ministero dell'Economia e Finanze.",
                    showarrow=False,
                    yref="paper",
                    y=mb * 0.9,
                    font={"color": "grey", "size": 9},
                )
            ],
        )
        watermark(f).show()
    bilancio_data = bilancio.loc[bilancio["Descrizione Programma"].isin(programmi + p2)]
    fig = make_subplots(
        rows=2,
        cols=1,
        # shared_xaxes=True,
        row_heights=[800, 1250],
        column_widths=[450],
        vertical_spacing=0.03,
        specs=[[{"type": "table"}], [{"type": "sunburst"}]],
    )
    fig.add_trace(
        go.Table(
            header=dict(
                values=[
                    "Descrizione Amministrazione",
                    "Descrizione Programma",
                    "Descrizione Azione",
                ]
                + ["Previsioni iniziali competenza"],
                font=dict(size=10),
                align="left",
            ),
            cells=dict(
                values=[
                    bilancio_data[k].tolist()
                    for k in [
                        "Descrizione Amministrazione",
                        "Descrizione Programma",
                        "Descrizione Azione",
                    ]
                    + ["Previsioni iniziali competenza"]
                ],
                align="left",
            ),
        ),
        row=2,
        col=1,
    )

    sb = px.sunburst(
        bilancio_data,
        path=[
            "Descrizione Amministrazione",
            "Descrizione Programma",
            "Descrizione Azione",
        ],
        values="Previsioni iniziali competenza",
        # color="Previsioni iniziali competenza",
        # color_continuous_scale='RdBu',
    )
    # sb.layout.coloraxis.showscale = False
    for t in sb.select_traces():
        fig.add_trace(t, row=1, col=1)
    fig.update_layout(
        height=1400,
        width=600,
        annotations=[
            dict(
                text="Fonte: Fonte: Open Data Ministero dell'Economia e Finanze.",
                showarrow=False,
                yref="paper",
                y=-0.02,
                font={"color": "grey", "size": 9},
            )
        ],
    )
    watermark(fig)
