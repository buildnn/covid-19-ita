import pandas as pd
from covid_health.prep_ecdc import parse_covid_world_data as pecdc
from covid_health.prep_owid import parse_covid_tests as ptests
from covid_health.fn.epidemic import calculate_epidemic_age
from covid_19_ita.utils import watermark

from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

pd.options.display.max_rows = 6


def get_covid_datasets():
    # ECDC covid data
    covid = pecdc()
    covid = covid.replace("United_States_of_America", "United States")
    # |   | time       | active_cases | n_deceased | geo         | geo_id | country_code |  population |
    # |--:|:-----------|-------------:|-----------:|:------------|:-------|:-------------|------------:|
    # | 0 | 2020-04-08 |           30 |          4 | Afghanistan | AF     | AFG          | 3.71724e+07 |
    # | 1 | 2020-04-07 |           38 |          0 | Afghanistan | AF     | AFG          | 3.71724e+07 |
    # | 2 | 2020-04-06 |           29 |          2 | Afghanistan | AF     | AFG          | 3.71724e+07 |
    # | 3 | 2020-04-05 |           35 |          1 | Afghanistan | AF     | AFG          | 3.71724e+07 |
    # | 4 | 2020-04-04 |            0 |          0 | Afghanistan | AF     | AFG          | 3.71724e+07 |

    epidemic_start = (
        covid.loc[covid.active_cases >= 100].groupby("geo").time.min()
    )
    epidemic_start.index = epidemic_start.index.str.replace("_", " ")
    # geo
    # Algeria                2020-03-29
    # Argentina              2020-03-26
    # Australia              2020-03-19
    #                           ...
    # United Arab Emirates   2020-03-31
    # United Kingdom         2020-03-13
    # Uzbekistan             2020-04-08
    # Name: time, Length: 65, dtype: datetime64[ns]

    tests = ptests()
    tests = tests.groupby(["time", "geo"], as_index=False).agg("mean")
    tests = tests[
        tests.geo.isin(
            tests.groupby("geo", as_index=False)
            .max()
            .nlargest(15, "tot_n_tests")
            .geo.values
        )
    ]
    tests["epidemic_start"] = epidemic_start.reindex(tests.geo.values).values
    tests["epidemic_age"] = (tests["time"] - tests["epidemic_start"]).dt.days
    # |   | time       | geo      | tot_n_tests | n_tests | tot_n_tests_pthab | n_tests_pthab | epidemic_start | epidemic_age |
    # |--:|:-----------|:---------|------------:|--------:|------------------:|--------------:|:---------------|-------------:|
    # | 0 | 2020-01-18 | US       |           4 |       4 |       1.20689e-05 |   1.20689e-05 | 2020-03-07     |          -49 |
    # | 1 | 2020-01-19 | US       |           4 |       0 |       1.20689e-05 |   0           | 2020-03-07     |          -48 |

    return covid, tests


def get_bilancio_datasets():

    bilancio_1 = (
        "https://raw.githubusercontent.com/buildnn/covid-19-ita/"
        "master/data/2020---Legge-di-Bilancio---02-Economia-e-Finanze---DPCM-22"
        "-09-2014-art3%20-%202020---Legge-di-Bilancio---02-E.csv"
    )
    bilancio_2 = (
        "https://raw.githubusercontent.com/buildnn/covid-19-ita/"
        "master/data/2020---Legge-di-Bilancio---15-Salute---DPCM-22-09-2014"
        "-art3%20-%202020---Legge-di-Bilancio---15-S.csv"
    )
    bilancio = pd.concat([pd.read_csv(bilancio_1), pd.read_csv(bilancio_2)])

    bilancio_prep = (
        bilancio
        .loc[
            bilancio["Descrizione Programma"].isin(programmi + p2),  # rows
            [  # cols
                "Descrizione Amministrazione",
                "Descrizione Programma",
                "Descrizione Azione",
                "Descrizione Missione",
                "Previsioni iniziali competenza",
            ]
        ]
        .groupby([
            "Descrizione Amministrazione",
            "Descrizione Programma",
            "Descrizione Missione",
            "Descrizione Azione",
        ]).sum()
        .sort_values(by=['Previsioni iniziali competenza'], ascending=False)
        .sort_index(level=[0, 1])
    )

    return bilancio, bilancio_prep


def plot(
    df, x, y, pl_kwargs, labels, title, update_layout_kwargs, line_shape=None
):
    fig = px.line(
        df,
        x=x,
        y=y,
        color="geo",
        template="plotly_white",
        title=title,
        labels=labels,
        line_shape=line_shape,
        **pl_kwargs
    )

    for n, trace in enumerate(fig.select_traces()):
        trace["line"]["width"] = 0.75
        trace["mode"] = "lines+markers"
        trace["marker"] = {"symbol": 133, "opacity": 0.5, "size": 3}

        trace = go.Scatter(
            x=trace["x"][-1:],
            y=trace["y"][-1:],
            name=trace["name"],
            text=[trace["name"]],
            showlegend=False,
            mode="markers",
            textposition="middle right",
            marker=dict(color=trace["line"]["color"]),
        )

        if trace["name"] in [
            "Italy",
            "South Korea",
            "China",
            "Canada",
            "Australia",
            "United States",
            "Germany",
            "United Kingdom",
            "Spain",
        ]:
            trace["mode"] = "markers+text"
        fig.add_trace(trace)

    update_kwa = dict(
        width=400,
        margin={"r": 20, "b": 180, "t": 80, "l": 70, "autoexpand": False},
        height=750,
        title={"x": 0.5},
        showlegend=False,
        legend=dict(orientation="v", x=0.0, y=1.0, title=None),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date" if x == "time" else "linear",
        ),
    )
    update_kwa.update(update_layout_kwargs)

    fig.update_layout(**update_kwa)
    watermark(fig)
    return fig
