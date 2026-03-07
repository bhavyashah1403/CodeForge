import plotly.express as px


def price_time_chart(df, time_col="datetime", price_col="spot_close"):
    if df.empty:
        return None
    return px.line(df.sort_values(time_col), x=time_col, y=price_col, title="Underlying Price")


def oi_volume_chart(df, time_col="datetime", oi_call="oi_CE", oi_put="oi_PE", vol_call="volume_CE", vol_put="volume_PE"):
    if df.empty:
        return None
    df2 = df.sort_values(time_col)
    fig = px.line(df2, x=time_col, y=[oi_call, oi_put], title="Open Interest: Call vs Put")
    return fig
