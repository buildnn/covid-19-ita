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
import warnings

# TARGET_DIR = "tmp"
TARGET_DIR = join(SITE_DIR, "figures", "tortuga", "II")

GDF_REG = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"


def get_es_maps():
    es_unit_value_map = dict(prep_eurostat.var["eurostat"]["unit"])
    es_geo_value_map = dict(prep_eurostat.var["eurostat"]["geo"])
    es_geo_value_map["DE"] = "<b>Germania</b>"
    es_geo_value_map["IT"] = "<b>Italia</b>"
    es_geo_value_map["FR"] = "<b>Francia</b>"
    es_geo_value_map["ITH1"] = "Bolzano"
    es_geo_value_map["ITH2"] = "Trento"
    es_geo_value_map["ITC2"] = "Valle d'Aosta"

    return es_unit_value_map, es_geo_value_map


def fig_a001():

    es_unit_value_map, es_geo_value_map = get_es_maps()
    es_facility_value_map = dict(prep_eurostat.var["eurostat"]["facility"])

    hlth_rs_bdsrg = prep_eurostat.parse_eurostat_dataset("hlth_rs_bdsrg")
    hlth_rs_bdsrg = hlth_rs_bdsrg.query("unit == 'P_HTHAB'").drop(columns=["unit"])

    # curative_beds = hlth_rs_bdsrg.query("facility == 'HBEDT_CUR'").drop(
    #     columns=["facility"]
    # )
    hsp_beds = hlth_rs_bdsrg.loc[
        hlth_rs_bdsrg["geo"].str.startswith("IT")
        | hlth_rs_bdsrg["geo"].isin(["DE", "FR"])
    ]

    with warnings.catch_warnings(record=True):
        hsp_beds["time"] = hsp_beds["time"].dt.year
        hsp_beds["facility"] = hsp_beds["facility"].replace(es_facility_value_map)
        hsp_beds["Regione"] = hsp_beds["geo"].replace(es_geo_value_map)

    # --- CHARTS ---
    subset = hsp_beds.query("time == 2001 | time == 2017")
    subset = subset[subset.facility.str.startswith("Avail")]
    subset["time"] = subset["time"].astype(str)
    
    subset["level"] = subset["geo"].apply(len)
    subset = subset.sort_values(by=["time", "level"])
    

    fig_a001 = px.bar(
        subset,
        x="Regione",
        y="value",
        hover_data=["geo"],
        color="time",
        category_orders={0: "2017", 1: "2001"},
        width=500,
        height=400,
        barmode="group",
        template="plotly_white",
        labels={"value": "Totale Posti Letto per 100.000 ab."},
        color_discrete_sequence=px.colors.qualitative.Dark24,
        title="<br><b>Totale Posti Letto nelle Strutture Ospedaliere</b></br>"
        '<span style="font-size: 12px;">Posti Letto '
        "per 100.000 abitanti: Confronto 2001 vs. 2017</span>",
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
                text="Fonte: Rielaborazione BuildNN & Tortuga da Eurostat",
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


def fig_a003():

    es_unit_value_map, es_geo_value_map = get_es_maps()
    es_isco08_value_map = dict(prep_eurostat.var["eurostat"]["isco08"])

    hlth_rs_prsrg = prep_eurostat.parse_eurostat_dataset("hlth_rs_prsrg")
    hlth_rs_prsrg = hlth_rs_prsrg.query("unit == 'P_HTHAB'").drop(columns=["unit"])

    # curative_beds = hlth_rs_prsrg.query("facility == 'HBEDT_CUR'").drop(
    #     columns=["facility"]
    # )
    hsp_pers = hlth_rs_prsrg.loc[
        hlth_rs_prsrg["geo"].str.startswith("IT")
        | hlth_rs_prsrg["geo"].isin(["DE", "FR"])
    ]

    with warnings.catch_warnings(record=True):

        hsp_pers["time"] = hsp_pers["time"].dt.year
        hsp_pers["isco08"] = hsp_pers["isco08"].replace(es_isco08_value_map)
        hsp_pers["Regione"] = hsp_pers["geo"].replace(es_geo_value_map)

    # --- CHARTS ---
    field = "isco08"
    cls = "Medical doctors"
    subset = hsp_pers.query("time == 2001 | time == 2017")
    subset = (
        subset[subset[field] == cls]
        .rename(columns={"value": cls})
        .drop(columns=[field])
    )
    subset["time"] = subset["time"].astype(str)

    subset["level"] = subset["geo"].apply(len)
    subset = subset.sort_values(by=["time", "level"])

    fig_a003 = px.bar(
        subset,
        x="Regione",
        y=cls,
        hover_data=["geo"],
        color="time",
        category_orders={0: "2001", 1: "2017"},
        range_y=(0, 550),
        width=500,
        height=400,
        barmode="group",
        template="plotly_white",
        labels={cls: "Medici per 100.000 ab."},
        color_discrete_sequence=px.colors.qualitative.Dark24,
        title="<br><b>Numero di Medici nelle Strutture Ospedaliere</b></br>"
        '<span style="font-size: 12px;">Medici '
        "per 100.000 abitanti: Confronto 2001 vs. 2017</span>",
    )
    fig_a003.add_shape(
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
    fig_a003.update_layout(
        margin=dict(l=50, r=20, t=80, b=150, autoexpand=False),
        legend=dict(orientation="h", y=-0.58, title=None),
        xaxis=dict(title=None),
        title=dict(x=0.5, y=0.96),
        annotations=[
            dict(
                text="Fonte: Rielaborazione BuildNN & Tortuga da Eurostat",
                font=dict(size=9, color="grey"),
                showarrow=False,
                xref="paper",
                yref="paper",
                y=-0.84,
            )
        ],
    )
    watermark(fig_a003)

    return fig_a003


def fig_a004():

    es_unit_value_map, es_geo_value_map = get_es_maps()
    es_isco08_value_map = dict(prep_eurostat.var["eurostat"]["isco08"])

    hlth_rs_prsrg = prep_eurostat.parse_eurostat_dataset("hlth_rs_prsrg")
    hlth_rs_prsrg = hlth_rs_prsrg.query("unit == 'P_HTHAB'").drop(columns=["unit"])

    # curative_beds = hlth_rs_prsrg.query("facility == 'HBEDT_CUR'").drop(
    #     columns=["facility"]
    # )
    hsp_pers = hlth_rs_prsrg.loc[
        hlth_rs_prsrg["geo"].str.startswith("IT")
        | hlth_rs_prsrg["geo"].isin(["DE", "FR"])
    ]

    with warnings.catch_warnings(record=True):

        hsp_pers["time"] = hsp_pers["time"].dt.year
        hsp_pers["isco08"] = hsp_pers["isco08"].replace(es_isco08_value_map)
        hsp_pers["Regione"] = hsp_pers["geo"].replace(es_geo_value_map)

    # --- CHARTS ---
    field = "isco08"
    cls = "Nurses and midwives"
    subset = hsp_pers.query("time == 2008 | time == 2016")
    subset = (
        subset[subset[field] == cls]
        .rename(columns={"value": cls})
        .drop(columns=[field])
    )
    subset["time"] = subset["time"].astype(str)

    subset["level"] = subset["geo"].apply(len)
    subset = subset.sort_values(by=["time", "level"])    

    fig_a004 = px.bar(
        subset,
        x="Regione",
        y=cls,
        hover_data=["geo"],
        color="time",
        category_orders={0: "2008", 1: "2016"},
        range_y=(0, 1060),
        width=500,
        height=400,
        barmode="group",
        template="plotly_white",
        labels={cls: "Personale per 100.000 ab."},
        color_discrete_sequence=px.colors.qualitative.Dark24,
        title="<br><b>Personale Infermieristico e Ostetrico</b></br>"
        '<span style="font-size: 12px;">Unità di Personale '
        "per 100.000 abitanti: Confronto 2008 vs. 2016</span>",
    )
    fig_a004.add_shape(
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
    fig_a004.update_layout(
        margin=dict(l=50, r=20, t=80, b=150, autoexpand=False),
        legend=dict(orientation="h", y=-0.58, title=None),
        xaxis=dict(title=None),
        title=dict(x=0.5, y=0.96),
        annotations=[
            dict(
                text="Fonte: Rielaborazione BuildNN & Tortuga da Eurostat",
                font=dict(size=9, color="grey"),
                showarrow=False,
                xref="paper",
                yref="paper",
                y=-0.84,
            )
        ],
    )
    watermark(fig_a004)

    return fig_a004


def fig_a005():
    medici_df = pd.read_csv(
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vRNSiOhlGO4r2Dh2cSr2zJbQ-iUfqqbQojs"
        "aTe4z1omzhuIjI_fzJCoD3EFNzgCeXMeX-3cVsZK1hZS/pub?output=csv"
    )
    medici_df = medici_df.query("Anno == 2017")
    medici_df = medici_df.dropna(subset=["Regione"])
    medici_df = medici_df.replace("Emilia_Romagna", "Emilia-Romagna")
    medici_df = medici_df.replace("Friuli_Ven_Giu", "Friuli-Venezia Giulia")
    medici_df = medici_df.replace("PA_bolzano", "P.A. Bolzano")
    medici_df = medici_df.replace("PA_trento", "P.A. Trento")
    medici_df = medici_df[medici_df.Regione != ""]
    medici_df.loc[
        medici_df.Adempiente.isna() | (medici_df.Adempiente == ""),
        "Adempiente"
    ] = "Non Sottoposta a Verifica"

    fig_a005 = px.bar(
        medici_df,
        x="Regione",
        y="LEA",
        # hover_data=["Adempiente"],
        color="Adempiente",  # subset.time.astype(str),
        color_discrete_map={
            "Non Sottoposta a Verifica": "#BAB0AC",
            "Non Adempiente": "#E45756",
            "Adempiente": "#54A24B",
        },
        # range_y=(0, 1060),
        width=500,
        height=400,
        # barmode="group",
        template="plotly_white",
        labels={"LEA": "Punteggio LEA"},
        color_discrete_sequence=px.colors.qualitative.Dark24,
        title="<br><b>Punteggi LEA (Livelli Essenziali di Assistenza)</b></br>"
        '<span style="font-size: 12px;">Anno 2017</span>',
    )
    fig_a005.add_shape(
        # Line Vertical
        dict(
            type="line",
            x0=-1.,
            y0=160,
            x1=21.,
            y1=160,
            line=dict(
                color="#D45113",
                width=1,
                # dash="dot",
            ),
            opacity=1.,
        )
    )
    fig_a005.update_layout(
        margin=dict(l=50, r=20, t=80, b=170, autoexpand=False),
        legend=dict(orientation="h", y=-0.78, title=None),
        xaxis=dict(title=None),
        title=dict(x=0.5, y=0.96),
    )
    fig_a005.add_annotation(
        text="Fonte: Rielaborazione BuildNN & Tortuga da Eurostat",
        font=dict(size=9, color="grey"),
        showarrow=False,
        xref="paper",
        yref="paper",
       y=-1.04,
    )
    fig_a005.add_annotation(
        x=-0.5,
        y=160,
        xref="x",
        yref="y",
        xanchor="left",
        yanchor="middle",
        text="<b>Livello Minimo</b>",
        showarrow=False,
        font=dict(
            family="Courier New, monospace",
            size=10,
            color="#ffffff"
            ),
        align="left",
        bordercolor="#c7c7c7",
        borderwidth=0,
        borderpad=0,
        bgcolor="#D45113",
        # opacity=0.75
    )

    watermark(fig_a005)
    return fig_a005


if __name__ == "__main__":

    fig_a001().write_html(
        join(TARGET_DIR, "fig_a001.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_a002().write_html(
        join(TARGET_DIR, "fig_a002.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_a003().write_html(
        join(TARGET_DIR, "fig_a003.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_a004().write_html(
        join(TARGET_DIR, "fig_a004.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
    fig_a005().write_html(
        join(TARGET_DIR, "fig_a005.html"),
        config={"displaylogo": False},
        include_plotlyjs="cdn",
    )
