import plotly.express as px

def line_chart(df, x, y, title: str = ""):
    fig = px.line(df, x=x, y=y, markers=True, title=title)
    fig.update_layout(hovermode="x unified")
    return fig

def bar_chart(df, x, y, title: str = ""):
    fig = px.bar(df, x=x, y=y, title=title)
    return fig
