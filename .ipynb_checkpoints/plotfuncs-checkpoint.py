import plotly.graph_objects as go
from plotly.subplots import make_subplots

from main import (
    mean_report_df,
    digitize_data)


def make_a_figure(data, index, columns, height):
    fig = make_subplots(
        rows=len(columns) // 2 + 1,
        cols=2,
        subplot_titles=columns,
    )

    scatters = [
        go.Bar(y=data[col], x=index, name=col) for col in columns
    ]
    for i, scatter in enumerate(scatters):
        i += 1
        if i % 2 == 0:
            c, r = 2, int(i / 2)
        else:
            c, r = 1, i // 2 + 1
        fig.add_trace(scatter, row=r, col=c)

    fig.update_layout(
        template="plotly_dark",
        font_color="green",
        height=height,
        margin=dict(
        l=50,
        r=50,
        b=10,
        pad=10,
    ),
        
    )
    return fig


def make_a_hitmap(dataframe, height=600):
    fig = go.Figure()
    columns = dataframe.columns
    fig.add_trace(
        go.Heatmap(
            z=dataframe.corr().values,
            x=columns,
            y=columns,
            colorscale="Viridis",
        )
    )
    fig.update_layout(
        title="CORRELATION",
        template="plotly_dark",
        font_color="green",
        height=height,
        margin=dict(
        l=50,
        r=50,
        b=10,
        t=50,
        pad=4
    ),
    )
    return fig


def make_a_weekly_heatmap(data_frame, column_groups):
    report_df = mean_report_df(data_frame, column_groups)
    return make_a_hitmap(report_df)

def make_a_daily_heatmap(data_frame, column_groups):
    report_df = digitize_data(data_frame, column_groups)
    return make_a_hitmap(report_df)

def weekly_figure(data_frame, column_groups):
    report_dict = mean_report_df(data_frame, column_groups)
    return make_a_figure(
        report_dict,
        report_dict.index,
        report_dict.columns,
        height=1600,
    )

def daily_figure(data_frame, column_groups):
    digitized = digitize_data(data_frame, column_groups)
    return make_a_figure(digitized, 
                         digitized.index, 
                         digitized.columns, 
                         height=1600)


# check_box = dcc.Checklist(
#     id="check_box",
#     options=[
#         {"label": "New York City", "value": "NYC"},
#         {"label": "Montréal", "value": "MTL"},
#         {"label": "San Francisco", "value": "SF"},
#     ],
#     value=["MTL", "SF"],
#     style={"width": "10%", "display": "block"},
# )