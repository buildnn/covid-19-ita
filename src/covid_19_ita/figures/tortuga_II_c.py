from os.path import join

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from covid_19_ita import SITE_DIR
from covid_19_ita.utils import watermark
from covid_health.ita import prep_istat, prep_pcm_dpc
from covid_health.utils import map_names

TARGET_DIR = join(SITE_DIR, "figures", "tortuga", "II")


labels = {
    "test_pthab": "Tamponi per 1000 ab.",
    "test_pdisch": "Tamponi per Dimesso/Guarito",
    "test_picu": "Tamponi per Paziente in Terapia Intensiva",
    "test_pdec": "Tamponi per Deceduto",
    "test_phosp": "Tamponi per Paziente Ospedalizzato",
    "mortality": "Decessi sul Totale Casi",
    "deaths_pthab": "Decessi Ufficiali COVID-19 per 1000 ab.",
    "deaths_phhab": "Decessi Ufficiali COVID-19 per 10.000 ab.",
    "pos_pthab": "Casi COVID-19 Attivi per 1000 ab.",
    "n_home_quarantine": "Isolamento Domiciliare",
    "n_intensive_care": "Ricoverati in Terapia Intensiva",
    "n_hospitalized": "Ospedalizzati (escluso T.I.)",
    "region": "Regione",
    "totale_positivi": "Casi Attivi",
    map_names("epidemic_age"): map_names("epidemic_age") + " (100° caso)",
}


def get_pop_covid_regions():
    # Popolazione
    prov = prep_istat.parse_istat_geodemo(
        "2019_pop_provinces"
    )  # restituisce la popolazione per provincia
    prov["province_code"] = prov["province_code"].astype(
        int
    )  # convertiamo il codice provincia in numero

    protez_civile = prep_pcm_dpc.parse_covid_data("dpc-province")  # Province
    protez_civile = protez_civile[
        ["region_code", "region", "province_code", "province"]
    ]
    protez_civile["province_code"] = protez_civile["province_code"].astype(
        int
    )  # convertiamo il codice provincia in numero
    protez_civile = protez_civile.drop_duplicates(["province_code"])
    protez_civile = protez_civile.set_index("province_code")

    prov["region_code"] = (
        protez_civile["region_code"].reindex(prov.province_code.values).values
    )
    prov = prov.groupby("region_code")["population"].sum()
    covid_data = prep_pcm_dpc.parse_covid_data("dpc-regions")
    covid_data["population"] = prov.reindex(
        covid_data["region_code"].values
    ).values

    #  Creation of cross DB KPIs
    covid_data["test_pthab"] = (
        covid_data.n_tested / (covid_data.population / 1000)
    ).round(2)
    covid_data["test_pdisch"] = (
        covid_data.n_tested / covid_data.n_discharged_recovered
    ).round(2)
    covid_data["test_picu"] = (
        covid_data.n_tested / covid_data.n_intensive_care
    ).round(2)
    covid_data["test_pdec"] = (
        covid_data.n_tested / covid_data.n_deceased
    ).round(2)
    covid_data["test_phosp"] = (
        covid_data.n_tested / covid_data.n_hospitalized
    ).round(2)
    covid_data["mortality"] = (
        covid_data.n_deceased / covid_data.tot_n_cases
    ).round(2)
    covid_data["deaths_pthab"] = (
        covid_data.n_deceased / (covid_data.population / 1000)
    ).round(2)
    covid_data["deaths_phhab"] = (
        covid_data.n_deceased / (covid_data.population / 10000)
    ).round(2)
    covid_data["pos_pthab"] = (
        (covid_data.totale_positivi / covid_data.population) * 1000
    ).round(2)

    covid_data["time"] = covid_data["time"].dt.floor("D")

    return covid_data


def fig_c001(y="test_pthab", regions=["Lombardia", "Veneto"]):
    data = get_pop_covid_regions()
    covid_lomb_ven = data[data.region.isin(regions)]
    ita_mean = data.groupby("time", as_index=False).mean()

    fig = px.line(
        map_names(covid_lomb_ven),
        x=map_names("time"),
        y=map_names(y),
        color=map_names("region"),
        template="plotly_white",
        labels=labels,
        width=600,
        height=450,
    )

    fig.update_traces(
        mode="lines", line=dict(width=1.0), marker=dict(symbol=134),
    )

    fig.add_trace(
        go.Scatter(
            x=ita_mean["time"],
            y=ita_mean[y],
            line=dict(dash="dot", color="firebrick"),
            mode="lines",
            name="Media ITA",
        ),
    )

    for trace in fig.data:
        fig.add_trace(
            go.Scatter(
                x=trace["x"][[-1]],
                y=trace["y"][[-1]],
                text=trace["name"],
                textposition="middle right",
                marker=dict(color=trace["line"]["color"]),
                mode="markers+text",
                name=trace["name"],
                showlegend=False,
            )
        )

    fig.add_annotation(
        font=dict(size=9, color="grey"),
        showarrow=False,
        yref="paper",
        xref="paper",
        text="Fonte: ISTAT, Dipartimento di Protezione Civile Italiana",
        y=-0.1,
        yanchor="top",
    )

    fig.update_layout(
        title=dict(text=f"<b>{labels[y]}: Lombardia e Veneto</b>", x=0.5,),
        xaxis=dict(
            range=[
                data["time"].min(),
                data["time"].max() + pd.to_timedelta(10, "d"),
            ],
            title=None,
        ),
        margin={"l": 60, "r": 30, "t": 100, "b": 100, "autoexpand": False},
        legend=dict(
            orientation="h",
            title=None,
            xanchor="center",
            x=0.5,
            y=-0.15,
            yanchor="top",
        ),
        dragmode=False,
    )

    watermark(fig)

    return fig


def fig_c002(regions=["Lombardia", "Veneto"], norm="fraction"):
    value_name = "Valore % sul Tot." if norm == "fraction" else "Valore"
    yformat = ".1%" if norm == "fraction" else ".0"
    data = get_pop_covid_regions()
    covid_lomb_ven = data[data.region.isin(regions)]
    covid_lomb_ven = covid_lomb_ven.melt(
        id_vars=["time", "region"],
        value_vars=["n_home_quarantine", "n_hospitalized", "n_intensive_care"],
        var_name="Variabile",
        value_name=value_name,
    )

    covid_lomb_ven["Variabile"] = covid_lomb_ven["Variabile"].replace(labels)

    fig = px.area(
        covid_lomb_ven.sort_values(by=["time", "Variabile"], ascending=False),
        x="time",
        y=value_name,
        color="Variabile",
        color_discrete_sequence=["#EF553B", "#FF7F0E", "#54A24B"],
        facet_col="region",
        labels=labels,
        groupnorm=norm,
        template="plotly_white",
    )
    fig.update_xaxes(title=None)
    fig.add_annotation(
        font=dict(size=9, color="grey"),
        showarrow=False,
        yref="paper",
        xref="paper",
        text="Fonte: ISTAT, Dipartimento di Protezione Civile Italiana",
        y=-0.15,
        yanchor="top",
    )
    fig.update_layout(
        title=dict(
            text=f"<br><b>Composizione dei Casi COVID-19 Attivi:"
            " Lombardia e Veneto</b></br>"
            f'<span style="font-size: 12px">{value_name} - Clicca sulle Voci '
            "nella Legenda per Selezionare o Deselezionare</span>",
            x=0.5,
            y=0.98,
        ),
        legend=dict(orientation="h", y=-0.2, yanchor="top", title=None),
        yaxis=dict(tickformat=yformat),
        margin={"l": 60, "r": 30, "t": 130, "b": 100, "autoexpand": False},
        dragmode=False,
        width=650,
        height=450,
    )
    watermark(fig)

    return fig


if __name__ == "__main__":
    fig_c001().write_html(
        join(TARGET_DIR, "fig_c001.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_c002(norm=None).write_html(
        join(TARGET_DIR, "fig_c002.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_c002().write_html(
        join(TARGET_DIR, "fig_c002_norm.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_c001(y="pos_pthab").write_html(
        join(TARGET_DIR, "fig_c004.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )