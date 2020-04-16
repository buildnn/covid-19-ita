from os.path import join
import pandas as pd

from covid_health.ita.prep_pcm_dpc import parse_covid_data as dpc

from covid_19_ita.utils import watermark
from covid_19_ita import SITE_DIR
from covid_19_ita.figures.tortuga import (
    bar_line_plot,
    prep_dpc_regions,
)
import plotly.express as px
import plotly.graph_objects as go
import warnings


# TARGET_DIR = "tmp"
TARGET_DIR = join(SITE_DIR, "figures", "tortuga", "II")


def get_veneto_lombardy_df():
    regions = dpc("dpc-regions")
    regions = regions[regions.region.isin(["Lombardia", "Veneto"])]
    regions.time = regions.time.dt.floor("d")
    regions

    with warnings.catch_warnings(record=True):
        regions = pd.concat(list(dateanchored(regions)))

    regions.sort_values(by="time")

    return regions


def dateanchored(df, by="region", anchor_date="2020-02-25"):
    for ix, group in df.groupby(by=by):
        for col in [
            "n_hospitalized",
            "n_intensive_care",
            "tot_n_hospitalized",
            "n_home_quarantine",
            "totale_positivi",
            "variazione_totale_positivi",
            "nuovi_positivi",
            "n_discharged_recovered",
            "n_deceased",
            "tot_n_cases",
            "n_tested",
        ]:
            anchor = group.loc[group.time == anchor_date, col].iloc[0]
            if anchor != 0:
                group[col + "_anchored"] = group[col] / anchor

        yield group


def plot_veneto_lombardy(df, y, title):
    x = "time"

    fig = px.line(
        df.round(2),
        x=x,
        y=y,
        color="region",
        width=600,
        height=400,
        template="plotly_white",
        labels={
            "tot_n_hospitalized_anchored": "N. Ospedalizzati," " 25 Feb = 1",
            "n_intensive_care_anchored": "N. Ricoveri in Terapia Intensiva,"
            " 25 Feb = 1",
            "time": "Data",
            "region": "Regione",
        },
        range_x=(
            pd.to_datetime("2020-02-25"),
            df.time.max() + pd.to_timedelta(7, "D"),
        ),
        line_shape="spline",
    )

    fig.update_traces(line=dict(width=1.0))

    for trace in fig.data:
        name = trace["name"]
        color = trace["line"]["color"]

        lom = df.loc[(df.time == df.time.max()) & (df.region == name)]

        fig.add_trace(
            go.Scatter(
                x=lom[x],
                y=lom[y],
                text=lom["region"],
                textposition="middle right",
                mode="markers+text",
                hoverinfo="skip",
                marker=dict(color=color),
            )
        )

    fig.update_layout(
        margin={"l": 40, "r": 20, "b": 40, "t": 80, "autoexpand": False},
        title=dict(text=title, x=0.5, y=0.96,),
        xaxis=dict(title=None),
        yaxis_tickformat="20",
        # legend=dict(orientation="h", yanchor="top", y=-.15, title=None),
        showlegend=False,
    )
    fig.add_annotation(
        text="Fonte: Dipartimento di Protezione Civile",
        font=dict(size=9, color="grey"),
        showarrow=False,
        xref="paper",
        yref="paper",
        y=-0.14,
    )
    watermark(fig)

    return fig


def fig_b001():
    fig = plot_veneto_lombardy(
        get_veneto_lombardy_df(),
        y="tot_n_hospitalized_anchored",
        title=(
            "<br><b>Andamento del Numero di Pazienti COVID-19 Ospedalizzati"
            '</b></br><span style="font-size: 11px;">Veneto e Lombardia '
            "- Proporzione rispetto al 25 Febbraio (25 Feb = 1)</span>"
        ),
    )
    return fig


def fig_b002():
    fig = plot_veneto_lombardy(
        get_veneto_lombardy_df(),
        y="n_intensive_care_anchored",
        title=(
            "<br><b>Andamento del N. Pazienti COVID-19 in Terapia Intensiva"
            '</b></br><span style="font-size: 11px;">Veneto e Lombardia '
            "- Proporzione rispetto al 25 Febbraio (25 Feb = 1)</span>"
        ),
    )
    return fig


def fig_b003():
    fig = plot_veneto_lombardy(
        get_veneto_lombardy_df(),
        y="n_tested_anchored",
        title=(
            "<br><b>Andamento del N. Tamponi COVID-19</b></br>"
            '<span style="font-size: 11px;">Veneto e Lombardia '
            "- Proporzione rispetto al 25 Febbraio (25 Feb = 1)</span>"
        ),
    )
    return fig


if __name__ == "__main__":

    fig_b001().write_html(
        join(TARGET_DIR, f"fig_b001.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_b002().write_html(
        join(TARGET_DIR, "fig_b002.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_b003().write_html(
        join(TARGET_DIR, "fig_b003.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
