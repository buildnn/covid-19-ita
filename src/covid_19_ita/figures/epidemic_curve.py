import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from covid_health.fn.epidemic import calculate_epidemic_age
from covid_health.ita import prep_pcm_dpc
from covid_health.utils import map_names

from covid_19_ita import HTML_DIR


HUE = "province"
X = "epidemic_age"
Y = "tot_n_cases"
QUERY = "epidemic_age >= 0"

EXPORT_DIR = os.path.join(HTML_DIR, "figures")


def build_simulation_trace(
    simulation, x_values, name, color, real_data, Y, **kwargs
):
    mask = simulation < real_data[Y].max()
    trace = go.Scatter(
        dict(
            x=x_values[mask],
            y=simulation[mask],
            # line=dict(color=color, width=0.5, dash="dot"),
            line=dict(color=color, width=0.5),
            name=name,
            # mode='lines+markers',
            mode="lines",
            **kwargs,
        )
    )
    return trace


def make_fig_010001():

    covid_data = prep_pcm_dpc.parse_covid_data("dpc-province")
    covid_data = covid_data.query(
        "province != 'In fase di definizione/aggiornamento'"
    )
    covid_data = covid_data.sort_values(["time", HUE])
    covid_data

    covid_data = covid_data.query(f"{Y} > 0")
    covid_data = covid_data.query(f"{X} >= 0")
    covid_data["time"] = covid_data["time"].astype(str)

    # -----------

    x_values = np.array(list(range(int(covid_data[X].max()))))

    doub_w = np.array(
        [int(100 * (2 ** (1 / 7)) ** i) for i in range(len(x_values))]
    )
    doub_d = np.array(
        [int(100 * (2 ** (1 / 1)) ** i) for i in range(len(x_values))]
    )
    doub_3d = np.array(
        [int(100 * (2 ** (1 / 3)) ** i) for i in range(len(x_values))]
    )

    range_x = (0, int(covid_data[X].max()) + 1)
    fig = px.line(
        map_names(covid_data.query(QUERY), language="it"),
        x=map_names("epidemic_age"),
        y=map_names("tot_n_cases"),
        color=map_names("region"),
        line_dash=map_names("province"),
        color_discrete_sequence=px.colors.qualitative.T10,
        template="plotly_white",
        range_x=range_x,
        hover_data=[map_names("time")],
        height=700,
        log_y=True,
        range_y=(100, covid_data.tot_n_cases.max() * 1.1),
        title="Crescita dei casi: Tutte le Regioni".ljust(36),
    )

    fig.add_traces(
        [
            build_simulation_trace(
                simulation, x_values, name, color, covid_data, Y
            )
            for simulation, name, color in zip(
                [doub_d, doub_3d, doub_w],
                ["2x ogni gg", "2x ogni 3gg", "2x ogni settimana"],
                ["#3C1518", "#A44200", "#D58936"],
            )
        ]
    )

    # fig = go.Figure()

    # BUTTONS
    button_layer_1_height = 1.12
    button_layer_2_height = 1.065

    but_yaxis_scale = dict(
        type="buttons",
        direction="right",
        pad={"r": 10, "t": 10},
        showactive=True,
        x=0.01,
        xanchor="left",
        y=1.07,
        yanchor="top",
        # direction="down",
        # pad={"r": 10, "t": 10},
        # showactive=False,
        # x=0.,
        # xanchor="left",
        # y=1.08,
        # yanchor="top",
        buttons=[
            dict(
                label="Scala Log",
                method="update",
                args=[
                    "Scala asse Y",
                    # {"visible": [True, True]},
                    {
                        "yaxis": {
                            "type": "log",
                            "title": "Tot. Casi (log)",
                            # "range": (2, 4),
                        },
                    },
                ],
            ),
            dict(
                label="Scala Lineare",
                method="update",
                args=[
                    "Scala asse Y",
                    # {"visible": [True, False]},
                    {"yaxis": {"title": "Tot. Casi", "type": "linear",},},
                ],
            ),
        ],
    )

    # but_hide_legend = dict(
    #     type = "buttons",
    #     direction="right",
    #     pad={"r": 10, "t": 10},
    #     showactive=True,
    #     x=0.13,
    #     xanchor="left",
    #     y=button_layer_2_height,
    #     yanchor="top",
    #     # active=0,
    #     # direction="down",
    #     # # pad={"r": 10, "t": 10},
    #     # # showactive=False,
    #     # x=0.22,
    #     # # xanchor="left",
    #     # y=1.16,
    #     # # yanchor="top",
    #     buttons=[
    #         dict(
    #             label="Visualizza Legenda",
    #             method="relayout",
    #             args=[
    #                 {"showlegend": True},
    #             ],
    #         ),
    #         dict(
    #             label="Nascondi Legenda",
    #             method="relayout",
    #             args=[
    #                 {"showlegend": False},
    #             ],
    #         ),
    #     ],
    # )
    traces_region = [
        trace["name"].split(", ")[0] for trace in fig.select_traces()
    ]
    simulations = traces_region[-3:]
    traces_region = pd.Series(traces_region[:-3])
    but_region = dict(
        type="buttons",
        direction="down",
        pad={"r": 10, "t": 10},
        showactive=True,
        x=1.88,
        # xanchor="left",
        # active=0,
        # y=button_layer_2_height,
        # yanchor="top",
        # direction="down",
        # pad={"r": 10, "t": 10},
        # showactive=False,
        # x=0.22,
        # xanchor="left",
        # y=1.08,
        # yanchor="top",
        buttons=list(
            [
                dict(
                    label="Tutte le Regioni",
                    method="update",
                    args=[
                        {
                            "visible": [True]
                            * (len(traces_region) + len(simulations))
                        },
                        {
                            "title": "Crescita dei casi: Tutte le Regioni".ljust(
                                36
                            )
                        },
                    ],
                ),
            ]
            + [
                dict(
                    label=region,
                    method="update",
                    args=[
                        {
                            "visible": [r == region for r in traces_region]
                            + [True] * len(simulations)
                        },
                        {
                            "title": "Crescita dei casi: {}".format(
                                region
                            ).ljust(36)
                        },
                    ],
                )
                for region in traces_region.unique()
            ]
        ),
    )

    fig.update_layout(
        margin=dict(t=100, b=120, l=30, r=70),
        xaxis_showgrid=True,
        yaxis_showgrid=False,
        height=940,
        updatemenus=[but_yaxis_scale, but_region],
        # annotations=[
        #     dict(
        #         text="Scala asse Y:",
        #         x=0,
        #         xref="paper",
        #         y=1.06,
        #         yref="paper",
        #         align="left",
        #         showarrow=False,
        #     ),
        # ],
        showlegend=False,
    )

    # Range selector
    fig.update_layout(
        xaxis=dict(
            # rangeselector=dict(
            #     buttons=list([
            #         dict(count=1,
            #              label="1m",
            #              step="month",
            #              stepmode="backward"),
            #         dict(count=6,
            #              label="6m",
            #              step="month",
            #              stepmode="backward"),
            #         dict(count=1,
            #              label="YTD",
            #              step="year",
            #              stepmode="todate"),
            #         dict(count=1,
            #              label="1y",
            #              step="year",
            #              stepmode="backward"),
            #         dict(step="all")
            #     ])
            # ),
            rangeslider=dict(visible=True),
            type="linear",
        ),
    )

    return fig


if __name__ == "__main__":
    fig = make_fig_010001()
    fig.write_html(os.path.join(EXPORT_DIR, "fig_010001.html"))
