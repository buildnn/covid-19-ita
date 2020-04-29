from os.path import join

import plotly.express as px
import plotly.graph_objects as go

from covid_19_ita import SITE_DIR
from covid_19_ita.figures.tortuga import (
    line_double_trace,
    prep_dpc_regions,
    prep_dpc_ita,
    prep_korea,
)
from covid_19_ita.utils import watermark

# TARGET_DIR = "tmp"
TARGET_DIR = join(SITE_DIR, "figures", "tortuga", "IV")


def fig_e001():
    regioni = prep_dpc_regions()
    id_vars = [
        "time",
        "country",
        "region_code",
        "region",
        "latitude",
        "longitude",
        "epidemic_start",
        "epidemic_age",
    ]
    value_vars = [
        "n_hospitalized",
        "n_intensive_care",
        # 'n_home_quarantine',
        #  'being_tested',
        "new_deceased",
        "new_discharged",
    ]
    hosp_melted = regioni.melt(id_vars=id_vars, value_vars=value_vars)
    hosp_melted

    f1 = (
        px.area(
            hosp_melted[
                hosp_melted.region.isin(["Lombardia", "Veneto"])
            ].replace(
                {
                    "n_hospitalized": "Ospedalizzati (no T.I.)",
                    "n_intensive_care": "Terapia Intensiva",
                    # 'n_home_quarantine',
                    # 'being_tested',
                    "new_deceased": "Decessi",
                    "new_discharged": "Dimessi/Guariti",
                }
            ),
            labels={"value": "Valore", "time": "Dara", "region": "Regione"},
            x="time",
            y="value",
            color="variable",
            color_discrete_sequence=px.colors.qualitative.T10,
            facet_col="region",
            template="plotly_white",
            title="<b>Tamponi vs Impatto COVID-19 sugli Ospedali</b><br>"
            '<span style="font-size: 12px;">Confronto tra Veneto e Lombardia'
            "</span>",
        )
        .update_layout(
            margin={"t": 100, "autoexpand": False},
            title=dict(y=0.92, x=0.5),
            width=820,
            height=450,
            yaxis=dict(title=None, tickformat="d"),
            legend=dict(orientation="h", title=None, y=-0.13),
            dragmode=False,
        )
        .update_xaxes(title=None)
    )

    f2 = px.bar(
        regioni[regioni.region.isin(["Lombardia", "Veneto"])],
        x="time",
        y="being_tested",
        color_discrete_sequence=["steelblue"],
        facet_col="region",
        opacity=0.5,
    ).update_traces(hoverinfo="skip").update_layout(dragmode=False)

    for n, trace in enumerate(f2.select_traces()):
        trace["name"] = "Tamponi Effettuati"
        if n == 0:
            trace["showlegend"] = True
        f1.add_trace(trace, 1, n + 1)

    f1.add_annotation(
        text="Fonte: Dipartimento di Protezione Civile",
        font=dict(size=9, color="grey"),
        showarrow=False,
        xref="paper",
        yref="paper",
        y=-0.28,
    )

    watermark(f1)

    return f1


def fig_e002():
    regioni = prep_dpc_regions()
    x = "time"
    y1 = "being_tested"
    y2 = "nuovi_positivi"
    y1_pre = "Tamponi Effettuati"
    y2_pre = "Nuovi Casi Positivi"
    xaxis_title = ""
    # xaxis_title="N. Giorni Trascorsi dal 100° Contagio",
    d1 = regioni.query("region == 'Lombardia'")
    d2 = regioni.query("region == 'Veneto'")

    fig = line_double_trace(
        [
            (d1[x], d1[y1], f"{y1_pre}: Lombardia", "firebrick", "#843433"),
            (d2[x], d2[y1], f"{y1_pre}: Veneto", "steelblue", "#144458"),
        ],
        [
            (d1[x], d1[y2], f"{y2_pre}: Lombardia", "firebrick"),
            (d2[x], d2[y2], f"{y2_pre}: Veneto", "steelblue"),
        ],
        main_line_mode="lines+text",
        label_each=52,
        secondary_line_width=1.0,
        secondary_line_dash="dot",
        title="<br><b>Numero di Tamponi Eseguiti vs Nuovi Casi COVID-19</b>"
        '</br><span style="font-size: 12;">Differenza tra Veneto e '
        "Lombardia</span>",
        xaxis_title=xaxis_title,
        primary_y_title="<b>Numero Tamponi Eseguiti</b>",
        secondary_y_title="<b>Totale Casi Positivi</b>",
        source="Fonte: Dipartimento di Protezione Civile Italiana",
        primary_y_kwargs={"range": (-300, 12000)},
        secondary_y_kwargs={"range": (-100, 4000)},
        layout_kwargs={"width": 600},
        source_y=-0.48,
    ).update_layout(
        margin={"b": 120},
        height=450,
        legend={"y": -0.2},
        dragmode=False,
        xaxis=dict(
            # rangeslider=dict(
            #     visible=True
            # ),
            # range=(0, 54)
        ),
    )

    return fig


def fig_e003():
    regioni = prep_dpc_regions().query("epidemic_age >= 0")
    d1 = regioni.query("region == 'Lombardia'")
    d2 = regioni.query("region == 'Veneto'")

    d1_y = d1.being_tested / (d1.nuovi_positivi + d1.new_discharged)
    d2_y = d2.being_tested / (d2.nuovi_positivi + d2.new_discharged)

    fig = line_double_trace(
        [
            (
                d1["epidemic_age"],
                d1_y,
                "N. Tamponi per Caso Gestito: Lombardia",
                "firebrick",
                "#843433",
            ),
            (
                d2["epidemic_age"],
                d2_y,
                "N. Tamponi per Caso Gestito: Veneto",
                "steelblue",
                "#144458",
            ),
        ],
        None,
        main_line_mode="lines+markers+text",
        label_each=1.5,
        title="<br><b>Numero di Tamponi per Caso COVID-19 Gestito</b>"
        '</br><span style="font-size: 12;">Casi COVID-19 Gestiti = Nuovi '
        "Positivi + Dimessi</span>",
        xaxis_title="N. Giorni Trascorsi dal 100° Caso Ufficiale",
        primary_y_title="<b>Numero Tamponi Eseguiti</b>",
        source="Fonte: Dipartimento di Protezione Civile Italiana",
        # primary_y_kwargs={"range": (-300, 12000)},
        # layout_kwargs={"width": 600},
        source_y=-0.46,
    ).update_layout(
        margin={"b": 120},
        width=800,
        height=450,
        legend=dict(orientation="h", y=-.24, x=.5, xanchor="center"),
        yaxis=dict(range=(0, 80)),
        dragmode=False,
    )

    return fig


if __name__ == "__main__":

    fig_e001().write_html(
        join(TARGET_DIR, "fig_e001.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )

    fig_e002().write_html(
        join(TARGET_DIR, "fig_e002.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )

    fig_e003().write_html(
        join(TARGET_DIR, "fig_e003.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
