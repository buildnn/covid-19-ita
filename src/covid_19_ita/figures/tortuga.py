import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from covid_19_ita.utils import watermark
from covid_health.ita import prep_pcm_dpc


tamponi_korea = (
    "https://docs.google.com/spreadsheets/d/"
    "1nKRkOwnGV7RgsMnsYE6l96u4xxl3ZaNiTluPKEPaWm8/export?format=csv&"
    "id=1nKRkOwnGV7RgsMnsYE6l96u4xxl3ZaNiTluPKEPaWm8&gid=306770783"
)
date_korea = (
    "https://docs.google.com/spreadsheets/d/"
    "1nKRkOwnGV7RgsMnsYE6l96u4xxl3ZaNiTluPKEPaWm8/export?format=csv&"
    "id=1nKRkOwnGV7RgsMnsYE6l96u4xxl3ZaNiTluPKEPaWm8&gid=9649165"
)


def decumulate(
    dataframe: pd.DataFrame, col, newcol, first_val: object = 0
) -> np.ndarray:
    series = dataframe[col]
    result = np.append(
        [first_val], series.iloc[1:].values - series.iloc[:-1].values
    )
    dataframe[newcol] = result
    return dataframe


def bar_line_plot(
    df,
    x="date_report",
    bary=[  # col_name, label, color, trace_kwargs
        ("new_positives", "Nuovi Casi", "#FF8A5B", {}),
        ("new_deaths", "Decessi", "#EA526F", {}),
        ("new_discharged", "Dimessi/Guariti", "#25CED1", {}),
    ],
    barmode="stack",
    liney=(
        "being_tested",
        "Test Effettuati",
        "firebrick",
        {"mode": "lines+markers"},
    ),
    yscale=100,
    secondaryy=False,
    y1_title="<b>N. Casi -- N. Test Effettuati/100</b>",
    y2_title="<b>N. Test Effettuati</b>",
    title="<br><b>Andamento del Contagio in Korea del Sud</b></br>"
    '<span style="font-size: 13px;">'
    " Casi Attivi, Dimessi/Guariti, Decessi e Test Effettuati</span>",
    fonte="Fonte: Korea Centers for Desease Control and Prevention",
):

    fig = make_subplots(specs=[[{"secondary_y": secondaryy}]])

    for col_name, label, color, trace_kwargs in bary:
        trace = (
            go.Bar(
                x=df[x],
                y=df[col_name],
                name=label,
                marker=dict(color=color),
                opacity=0.75,
                **trace_kwargs
            ),
        )
        fig.add_trace(trace[0], secondary_y=False)

    fig.update_layout(barmode=barmode)

    # -- TESTS
    col_name, label, color, trace_kwargs = liney
    line_trace = go.Scatter(
        x=df[x],
        y=df[col_name] / yscale,
        name=label,
        line=dict(color=color, width=0.75,),
        marker=dict(symbol=134),
        **trace_kwargs
    )
    fig.add_trace(line_trace, secondary_y=secondaryy)

    if secondaryy:
        fig.update_yaxes(
            title=dict(text=y2_title, font=dict(size=11)),
            range=(0, (df[liney[0]] / yscale).max() * 1.1),
            secondary_y=True,
            showgrid=False,
        )

    fig.update_yaxes(
        title=dict(text=y1_title, font=dict(size=11)), secondary_y=False
    )

    fig.update_layout(
        margin={"t": 80, "l": 40, "r": 20, "autoexpand": False},
        title=dict(text=title, x=0.5,),
        template="plotly_white",
        width=750,
        height=500,
        legend=dict(orientation="h"),
        annotations=[
            dict(
                text=fonte,
                font=dict(size=9, color="grey"),
                showarrow=False,
                xref="paper",
                yref="paper",
                y=-0.24,
            )
        ],
    )

    watermark(fig)

    return fig


def prep_dpc_regions():
    regioni = prep_pcm_dpc.parse_covid_data("dpc-regions")
    regioni.time = regioni.time.dt.floor("d")
    regioni["active"] = (
        regioni["tot_n_cases"]
        - regioni["n_discharged_recovered"]
        - regioni["n_deceased"]
    )
    regioni = regioni[~regioni.region.str.startswith("In fase di")]
    regioni["region"] = regioni["region"].str.strip()

    ssets = []
    with warnings.catch_warnings(record=True):
        for ix, sset in regioni.groupby("region"):
            sset["being_tested"] = np.append(
                [0], sset["n_tested"].values[1:] - sset["n_tested"].values[:-1]
            )
            sset.loc[sset["being_tested"].values < 0, "being_tested"] = 0
            sset = decumulate(sset, "n_deceased", "new_deceased")
            sset = decumulate(sset, "n_discharged_recovered", "new_discharged")
            ssets.append(sset.sort_values("time"))
    regioni = pd.concat(ssets)
    return regioni


def prep_dpc_ita():
    ita_df = (
        prep_dpc_regions()
        .groupby("time", as_index=False)[
            [
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
                "being_tested",
            ]
        ]
        .sum()
    )
    ita_df = decumulate(ita_df, "n_deceased", "new_deceased")
    ita_df = decumulate(ita_df, "n_discharged_recovered", "new_discharged")
    ita_df["active"] = (
        ita_df["tot_n_cases"]
        - ita_df["n_discharged_recovered"]
        - ita_df["n_deceased"]
    )
    ita_df["epidemic_start"] = ita_df[ita_df.tot_n_cases >= 100].time.min()
    ita_df["epidemic_age"] = (
        ita_df["time"] - ita_df["epidemic_start"]
    ).dt.days
    ita_df["second_disch_totest"] = np.append(
        [0] * 14, ita_df["new_discharged"].iloc[:-14]
    )
    return ita_df


def prep_korea():
    korea_df = pd.read_csv(tamponi_korea).iloc[:, :-2]
    korea_df = korea_df.replace({"": np.nan})
    korea_df = korea_df.astype(
        {
            "positive": float,
            "death": float,
            "discharged": float,
            "unknown": float,
        }
    )
    korea_df["date_report"] = pd.to_datetime(korea_df["date_report"])
    korea_df = korea_df.rename(columns={"unknown": "being_tested"})
    korea_df = korea_df.groupby("date_report", as_index=False).agg(
        {
            "suspected cases": "max",
            "positive": "max",
            "discharged": "max",
            "death": "max",
            "negative": "max",
            "being_tested": "sum",
        }
    )
    korea_df["active"] = (
        korea_df["positive"] - korea_df["death"] - korea_df["discharged"]
    )
    korea_df["epidemic_start"] = korea_df[korea_df.positive >= 100][
        "date_report"
    ].min()
    korea_df["epidemic_age"] = (
        korea_df["date_report"] - korea_df["epidemic_start"]
    ).dt.days
    korea_df = korea_df.sort_values("date_report", ascending=True)
    korea_df = decumulate(korea_df, "positive", "new_positives")
    korea_df = decumulate(korea_df, "death", "new_deaths")
    korea_df = decumulate(korea_df, "discharged", "new_discharged")
    korea_df["second_disch_totest"] = np.append(
        [0] * 14, korea_df["new_discharged"].iloc[:-14]
    )
    return korea_df


def line_double_trace(
    elements,
    secondary_elements=None,
    main_line_mode="lines+markers+text",
    secondary_line_dash="solid",
    main_line_width=1.75,
    secondary_line_width=0.75,
    label_format="<b>{:.0f}</b>",
    label_each=3,
    primary_y_title="<b>Numero Tamponi Eseguiti</b>",
    secondary_y_title="<b>Nuovi Casi Positivi</b>",
    title="<br><b>Numero di Tamponi Eseguiti vs Nuovi Casi COVID-19</b></br>"
    '<span style="font-size: 12;">Differenza tra italia e Korea del '
    "Sud</span>",
    xaxis_title="N. Giorni Trascorsi dal 100° Caso Ufficiale",
    source="Fonte: Dipartimento di Protezione Civile Italiana, "
    "Korea Centers for Desease Control and Prevention</p>",
    source_y=-0.49,
    primary_y_kwargs={},
    secondary_y_kwargs={},
    layout_kwargs={},
):
    """
    elements = [(x: array, y: array, name: str, color: str, textcolor: str)]
    secondary_elements = [(x: array, y: array, name: str, color: str)]
    """

    fig = make_subplots(
        specs=[[{"secondary_y": True if secondary_elements else False}]]
    )

    for x, y, name, color, textcolor in elements:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                text=[
                    label_format.format(x) if n % label_each == 0 else ""
                    for n, x in enumerate(y)
                ],
                name=name,
                # --- LINE
                textposition="top center",
                textfont=dict(color=textcolor),
                line=dict(color=color, width=main_line_width,),
                mode=main_line_mode,
                marker=dict(color=color),
                line_shape="spline",
                # ---
                opacity=0.75,
                showlegend=True,
            )
        )

    if secondary_elements:
        for x, y, name, color in secondary_elements:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    name=name,
                    # --- LINE
                    line=dict(
                        color=color,
                        width=secondary_line_width,
                        dash=secondary_line_dash,
                    ),
                    mode="lines",
                    line_shape="spline",
                    # ---
                    opacity=0.75,
                    showlegend=True,
                ),
                secondary_y=True,
            )

    # Primary
    fig.update_yaxes(
        title=dict(text=primary_y_title, font=dict(size=11)),
        secondary_y=False,
        **primary_y_kwargs
    )

    # Secondary
    fig.update_yaxes(
        title=dict(text=secondary_y_title, font=dict(size=11)),
        secondary_y=True,
        showgrid=False,
        **secondary_y_kwargs
    )

    _layout_kwargs_std = dict(
        title=dict(text=title, x=0.5, y=0.98),
        margin={"l": 40, "r": 10, "t": 80, "b": 140, "autoexpand": False},
        template="plotly_white",
        width=700,
        height=450,
        showlegend=True,
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
        # yaxis=dict(range=(0, 400)),
        xaxis=dict(title=xaxis_title),
        annotations=[
            dict(
                font=dict(size=9, color="grey"),
                showarrow=False,
                yref="paper",
                xref="paper",
                text=source,
                y=source_y,
            )
        ],
    )
    _layout_kwargs_std.update(layout_kwargs)

    fig.update_layout(**_layout_kwargs_std)
    watermark(fig)

    return fig
