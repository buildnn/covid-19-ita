def watermark(fig, logo_y=None, annot_y=None, logo_h=None):
    margin = fig.layout["margin"]
    b = margin["b"]
    t = margin["t"]
    l = margin["l"]
    r = margin["r"]

    b = b if b else 0
    t = t if t else 0
    l = l if l else 0
    r = r if r else 0

    w = fig["layout"]["width"]
    h = fig["layout"]["height"]

    font_size = 7
    logo_h = 30 if not logo_h else logo_h
    logo_size_x = logo_h / (w - l)
    annot_x = 1.0 + 4 / w

    logo_y = 1 + 36 / (h - t - b) if not logo_y else logo_y
    annot_y = 1 + 22 / (h - t - b) if not annot_y else annot_y

    logo = dict(
        source="https://media-exp1.licdn.com/dms/image/C4D0BAQFsEw0kedrArQ/"
        "company-logo_200_200/0?e=1593043200&v=beta&"
        "t=UJ-7KQbrKQz-6NUbBCP706EzxNQVzt9ZftyH_Z46oNo",
        xref="paper",
        yref="paper",
        x=1.0,
        y=logo_y,
        sizex=logo_size_x,
        sizey=30,
        xanchor="right",
        yanchor="bottom",
    )

    annot = dict(
        text=f'<span  style="font-size: {font_size}px">by '
        '<a href="https://www.buildnn.com">BuildNN</a></span>',
        showarrow=False,
        xref="paper",
        yref="paper",
        x=annot_x,
        y=annot_y,
        xanchor="right",
        yanchor="bottom",
    )

    fig.update_layout(
        images=[logo], annotations=list(fig["layout"]["annotations"]) + [annot]
    )
    return fig
