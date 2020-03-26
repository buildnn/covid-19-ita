import os 
import pandas as pd
import numpy as np
from covid_health.prep_eurostat import parse_eurostat_dataset 
from covid_health.ita import prep_pcm_dpc, prep_salutegov 
from covid_health.utils import map_names

from covid_19_ita import HTML_DIR
import plotly.express as px


EXPORT_DIR = os.path.join(HTML_DIR, "figures")


if __name__ == "__main__":
    hospital_beds = prep_salutegov.parse_dataset("hospital_beds_by_discipline_hospital")
    hospital_beds.region_code = hospital_beds.region_code.str[:2]
    hospital_beds = (
        hospital_beds
        .query("discipline == 'TERAPIA INTENSIVA' & time == '2018'")
        .astype({"region_code": int})
        .groupby("region_code")
        .agg({"tot_n_hospital_bed": "sum"})
    )

    covid_data_reg = prep_pcm_dpc.parse_covid_data("dpc-regions")
    covid_data_reg['region_code'].unique()
    covid_data_reg['intensive_care_beds'] = hospital_beds.reindex(covid_data_reg['region_code'].values.astype(int)).values


    snap = covid_data_reg#[covid_data_reg.data == covid_data_reg.data.max()]
    snap["saturazione_TI"] = snap['n_intensive_care'] / snap['intensive_care_beds']
    snap['time'] = snap['time'].dt.floor("D").astype(str)

    col_map = {
        "region": "Regione",
        "saturazione_TI": "Saturazione Terapia Intensiva (con capacità 2018)",
    }

    fig = px.bar(
        map_names(snap), 
        x=map_names("region"),
        y=map_names("saturazione_TI"),
        color=map_names("saturazione_TI"),
        animation_frame="Data",
        animation_group=map_names("region"),
        color_continuous_scale=px.colors.cyclical.IceFire[2:-2],
        range_y=[0, 1.4],
        color_continuous_midpoint=.5,
        template="plotly_dark",
        range_color=[0, 1.3],
    )

    fig = fig.update_layout(
        xaxis_title="",
        yaxis_tickformat = '%')
    fig.layout.coloraxis.showscale = False


        # Range selector
    fig.update_layout(
        images=[
            dict(
                source="https://media-exp1.licdn.com/dms/image/C4D0BAQFsEw0kedrArQ/company-logo_200_200/0?e=1593043200&v=beta&t=UJ-7KQbrKQz-6NUbBCP706EzxNQVzt9ZftyH_Z46oNo",
                xref="paper",
                yref="paper",
                x=1,
                y=.95,
                sizex=0.1,
                sizey=0.1,
                xanchor="right",
                yanchor="bottom",
            )
        ],
        annotations=[
            dict(
                text='by <a href="https://www.buildnn.com">BuildNN</a>',
                # size=8,
                showarrow=False,
                xref="paper",
                yref="paper",
                x=1,
                y=.91,
                # sizex=0.1, sizey=0.1,
                xanchor="right",
                yanchor="bottom",
            ),
        ],
    )

    fig.write_html(
        os.path.join(EXPORT_DIR, "fig_010004.html"),
        config={
            "scrollZoom": True,
            "doubleClick": False,
            "showAxisDragHandles": False,
            # "displayModeBar": True,
            "doubleClick": "reset+autosize",
            "displaylogo": False,
            # 'hoverCompareCartesian': True,
        },
    )