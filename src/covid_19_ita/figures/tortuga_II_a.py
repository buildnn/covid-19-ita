from os.path import join
import pandas as pd
import numpy as np

# import geopandas as gpd
from covid_health.ita import prep_salutegov

# from covid_health.ita import prep_istat
from covid_health import prep_eurostat

from covid_19_ita.utils import watermark
from covid_19_ita import SITE_DIR
import plotly.express as px

# import plotly.graph_objects as go
# import warnings

# TARGET_DIR = "tmp"
TARGET_DIR = join(SITE_DIR, "figures", "tortuga", "II")

GDF_REG = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"


def get_es_maps():
    es_unit_value_map = dict(prep_eurostat.var["eurostat"]["unit"])
    es_facility_value_map = dict(prep_eurostat.var["eurostat"]["facility"])
    es_geo_value_map = dict(prep_eurostat.var["eurostat"]["geo"])
    es_geo_value_map["DE"] = "<b>Germania</b>"
    es_geo_value_map["IT"] = "<b>Italia</b>"
    es_geo_value_map["FR"] = "<b>Francia</b>"
    es_geo_value_map["ITH1"] = "Bolzano"
    es_geo_value_map["ITH2"] = "Trento"
    es_geo_value_map["ITC2"] = "Valle d'Aosta"

    return es_unit_value_map, es_facility_value_map, es_geo_value_map


def fig_a001():

    es_unit_value_map, es_facility_value_map, es_geo_value_map = get_es_maps()

    hlth_rs_bdsrg = prep_eurostat.parse_eurostat_dataset("hlth_rs_bdsrg")
    hlth_rs_bdsrg = hlth_rs_bdsrg.query("unit == 'P_HTHAB'").drop(columns=["unit"])

    # curative_beds = hlth_rs_bdsrg.query("facility == 'HBEDT_CUR'").drop(
    #     columns=["facility"]
    # )
    hsp_beds = hlth_rs_bdsrg.loc[
        hlth_rs_bdsrg["geo"].str.startswith("IT")
        | hlth_rs_bdsrg["geo"].isin(["DE", "FR"])
    ]

    hsp_beds["time"] = hsp_beds["time"].dt.year
    hsp_beds["facility"] = hsp_beds["facility"].replace(es_facility_value_map)
    hsp_beds["Regione"] = hsp_beds["geo"].replace(es_geo_value_map)

    # --- CHARTS ---
    subset = hsp_beds.query("time == 2001 | time == 2017")
    subset = subset[subset.facility.str.startswith("Avail")]

    fig_a001 = px.bar(
        subset,
        x="Regione",
        y="value",
        hover_data=["geo"],
        color=subset.time.astype(str),
        width=500,
        height=400,
        barmode="group",
        template="plotly_white",
        labels={"value": "Totale Posti Letto per 100.000 ab."},
        color_discrete_sequence=px.colors.qualitative.Dark24,
        title="<br><b>Totale Posti Letto nelle Strutture Ospedaliere</b></br>"
        '<span style="font-size: 12px;">Posti Letto '
        "per 100.000 abitanti: Confronto 2011 vs. 2017</span>",
    )
    fig_a001.add_shape(
        # Line Vertical
        dict(
            type="line",
            x0=2.5,
            y0=-10,
            x1=2.5,
            y1=900,
            line=dict(
                color="grey",
                width=1,
                # dash="dot",
            ),
            opacity=0.5,
        )
    )
    fig_a001.update_layout(
        margin=dict(l=50, r=20, t=80, b=150, autoexpand=False),
        legend=dict(orientation="h", y=-0.58, title=None),
        xaxis=dict(title=None),
        title=dict(x=0.5, y=0.96),
        annotations=[
            dict(
                text="Fonte: Rielaborazione BuildNN & Tortuga da Ministero della Salute",
                font=dict(size=9, color="grey"),
                showarrow=False,
                xref="paper",
                yref="paper",
                y=-0.84,
            )
        ],
    )
    watermark(fig_a001)

    return fig_a001


def fig_a002():

    # -- PHARMA
    pharma = (
        prep_salutegov.parse_dataset("pharmacies")
        .groupby("region_code")[["pharmacy_code"]]
        .nunique()
        .reset_index()
        .rename(columns={"pharmacy_code": "n_pharmacies"})
    )
    asl = (
        prep_salutegov.parse_dataset("asl_comuni_pop")
        .replace("", np.nan)
        .dropna(subset=["region_code"])
    )
    asl["TOTALE"] = (
        asl["TOTALE"]
        .str.replace(".", "")
        .str.replace(",", ".")
        .replace("", np.nan)
        .astype(float)
    )
    pop = asl.groupby(["region_code"]).agg(
        population=pd.NamedAgg("TOTALE", "sum"), region=pd.NamedAgg("region", "first"),
    )

    pharma["population"] = pop.reindex(pharma["region_code"].values)[
        "population"
    ].values
    pharma["region"] = (
        pop.reindex(pharma["region_code"].values)["region"].str.title().values
    )
    pharma.loc[pharma.region_code == "04", "region"] = "Trentino-Alto Adige/Südtirol"
    pharma["hab_per_pharma"] = (
        (pharma["population"] / pharma["n_pharmacies"]).round(0).astype(int)
    )

    fig_a002 = px.choropleth(
        pharma,
        geojson=GDF_REG,
        color="hab_per_pharma",
        hover_data=["region", "n_pharmacies", "population"],
        locations="region_code",
        # range_color=(0, 3.5),
        center={"lat": 42.65, "lon": 12.4},
        featureidkey="properties.reg_istat_code",
        projection="mercator",
        template="plotly_dark",
        color_continuous_scale=px.colors.diverging.Temps,
        labels={
            "region_code": "Cod. Regione",
            "region": "Regione",
            "hab_per_pharma": "Ab. per Farmacia",
            "n_pharmacies": "Numero Farmacie",
            "population": "Numero Abitanti",
        },
        # line_shape="spline",
    )
    fig_a002.update_geos(fitbounds="locations", visible=False).update_layout(
        width=600, height=600
    )

    fig_a002.update_layout(
        margin=dict(l=80, r=140, b=80, t=100, autoexpand=False),
        title=dict(
            text="<br><b>Abitanti per Farmacia</b></br>"
            '<span style="font-size: 11px;">Anno 2018 - Meno è Meglio</span>',
            x=0.5,
            y=0.96,
        ),
        xaxis=dict(title=None),
        yaxis_tickformat="20",
        legend=dict(orientation="h", yanchor="top", y=-0.15, title=None),
        # showlegend=False,
        annotations=[
            dict(
                text="Fonte: Rielaborazione BuildNN & Tortuga da Ministero della Salute",
                font=dict(size=9, color="grey"),
                showarrow=False,
                xref="paper",
                yref="paper",
                y=-0.0,
            )
        ],
    )

    watermark(fig_a002)

    return fig_a002


if __name__ == "__main__":

    fig_a001().write_html(
        join(TARGET_DIR, "fig_a001.html"), config={"displaylogo": False}
    )
    fig_a002().write_html(join(TARGET_DIR, "fig_a002.html"), include_plotlyjs="cdn")

