import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from omegaconf import OmegaConf as omg

# TODO REFRESH
# LISTS TXT
# START USING

from main import (
    get_column_groups,
    get_frame_time_period,
    get_words_count_dict,
    init_data,
    pull_data_frame_from_google,
    get_local_data_frame,
)

from plotfuncs import (
    make_a_weekly_heatmap,
    make_a_daily_heatmap,
    weekly_figure,
    daily_figure,
    make_figures_words,
)

from textfuncs import get_last_text_records
from styles import style, text_style, text_style_normal

cfg = omg.load("./config.yaml")
banner = cfg.banner
slider_step = cfg.slider_step

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

frame, colulmn_groups = init_data(90)


slider = dcc.Slider(
    id="day-slider",
    min=0,
    max=len(frame.index),
    value=len(frame.index),
    marks={str(i): str(i) for i in range(0, frame.shape[0], slider_step)},
)

app.layout = dbc.Container(
    [
        html.H3(f"{banner}"),
        html.Div(id="days_ago", style=text_style),
        # className="p-5",
        slider,
        # check_box,
        html.Div(id="tab-content"),
        dbc.Button(
            "Load last records",
            color="primary",
            block=True,
            id="button_load_df",
            className="two columns",
        ),
        html.Div(id="num_records", style=text_style),
        dbc.Tabs(
            id="tabs",
            active_tab="daily_tab",
            children=[
                dbc.Tab(
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                id="free_flow_tab",
                                style=text_style_normal,
                                className="six columns",
                            ),
                            html.Div(
                                dcc.Graph(
                                    id="graph-count",
                                ),
                                id="free_flow_tab_list",
                                style=text_style_normal,
                                className="six columns",
                            ),
                        ],
                    ),
                    label="LAST RECORDS",
                    tab_id="free_flow_tab",
                    style=text_style_normal,
                ),
                dbc.Tab(
                    children=[
                        dcc.Graph(id="graph-all"),
                        dcc.Graph(
                            id="graph-heatmap-daily",
                        ),
                    ],
                    label="DAILY",
                    tab_id="daily_tab",
                    style=text_style_normal,
                ),
                dbc.Tab(
                    children=[
                        dcc.Graph(
                            id="graph-weekly",
                        ),
                        dcc.Graph(
                            id="graph-heatmap-weekly",
                        ),
                    ],
                    label="WEEKLY",
                    tab_id="weekly-tab",
                    style=text_style_normal,
                ),
            ],
        ),
    ],
    fluid=True,
    style=style,
)


@app.callback(
    Output("num_records", "children"),
    [Input("button_load_df", "n_clicks")],
)
def pull_the_data(n_clicks):
    pull_data_frame_from_google()
    frame = get_local_data_frame()
    return f"num records {frame.shape[0]}"


@app.callback(
    [
        Output("graph-all", "figure"),
        Output("graph-weekly", "figure"),
        Output("graph-heatmap-daily", "figure"),
        Output("graph-heatmap-weekly", "figure"),
        Output("free_flow_tab", "children"),
        Output("days_ago", "children"),
        Output("graph-count", "figure"),
    ],
    [Input("day-slider", "value")],
)
def updtae_plots(selected_time):
    ago = int(selected_time)
    print(selected_time)
    df = get_frame_time_period(frame, window_start=int(ago))
    column_groups = get_column_groups(df)
    words_count_dict, _ = get_words_count_dict(
        frame[column_groups["@textlist"]]
    )

    get_plots = [
        daily_figure,
        weekly_figure,
        make_a_daily_heatmap,
        make_a_weekly_heatmap,
    ]
    return (
        *[f(df, column_groups) for f in get_plots],
        get_last_text_records(frame, column_groups, ago - 1),
        f" Time period: {int(selected_time) } days",
        make_figures_words(words_count_dict),
    )


# @app.callback(Output("tab-content", "children"), [Input("tabs", "value")])
# def render_content(tab):
#     if tab == "tab-1":
#         return html.Div([html.H3("Tab content 1")])
#     elif tab == "tab-2":
#         return html.Div([html.H3("Tab content 2")])


if __name__ == "__main__":
    app.run_server(debug=True)
