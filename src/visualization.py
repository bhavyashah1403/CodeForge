import plotly.express as px
import plotly.graph_objects as go


def price_time_chart(df, time_col="datetime", price_col="spot_close"):
    if df.empty:
        return None
    return px.line(df.sort_values(time_col), x=time_col, y=price_col, title="Underlying Price")


def oi_time_chart(df, time_col="datetime", oi_call="oi_CE", oi_put="oi_PE"):
    if df.empty:
        return None
    df2 = df.sort_values(time_col)
    fig = go.Figure()
    if oi_call in df2.columns:
        fig.add_trace(go.Scatter(x=df2[time_col], y=df2[oi_call], mode="lines", name="Call OI"))
    if oi_put in df2.columns:
        fig.add_trace(go.Scatter(x=df2[time_col], y=df2[oi_put], mode="lines", name="Put OI"))
    fig.update_layout(title="Open Interest: Call vs Put", xaxis_title=time_col, yaxis_title="Open Interest")
    return fig


def volume_time_chart(df, time_col="datetime", vol_call="volume_CE", vol_put="volume_PE"):
    if df.empty:
        return None
    df2 = df.sort_values(time_col)
    fig = go.Figure()
    if vol_call in df2.columns:
        fig.add_trace(go.Bar(x=df2[time_col], y=df2[vol_call], name="Call Volume", marker_color="green"))
    if vol_put in df2.columns:
        fig.add_trace(go.Bar(x=df2[time_col], y=df2[vol_put], name="Put Volume", marker_color="red"))
    fig.update_layout(barmode="group", title="Trading Volume: Call vs Put", xaxis_title=time_col, yaxis_title="Volume")
    return fig
