import dash
import dash_core_components as dcc

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go


import plotly.express as px

from main import (
    pull_data_frame_from_google,
    get_local_data_frame,
    get_column_groups,
    get_last_text,
    get_frame_time_period,
    get_words_list_dict,
    init_data,
)

from plotfuncs import (make_a_weekly_heatmap, 
                      make_a_daily_heatmap, 
                      weekly_figure, 
                      daily_figure)


from styles import style, text_style, text_style_normal

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
frame, colulmn_groups = init_data(60)


# UPDATE TEXT
text_str = ""

text = []
last_text = get_last_text(frame[colulmn_groups["@text"]])
for col in last_text:
    t = last_text[col]
    if len(t) > 2:
        if len(t.split(".")) > 2:
            text.append("\n* **" + col.upper() + "**")
            # text.append("\n > -")
            text.append(
                " ".join(
                    [
                        " \n  *" + s + "\n"
                        for s in t.split(".")
                        if len(s) > 2
                    ]
                )
            )
        else:
            text.append("\n* **" + col.upper() + "**")
            text.append(">" + t)

text_str = dcc.Markdown(children="\n".join(text))


slider = dcc.Slider(
    id="day-slider",
    min=0,
    max=len(frame.index),
    value=len(frame.index),
    marks={str(i): str(i) for i in range(frame.shape[0])},
)


markdown_text = """
#### Dash and Markdown
*A lot of text*
"""


app.layout = dbc.Container(
    # html.Div(
    [
        dbc.Alert("Hello Bootstrap!", color="success"),
        dcc.Markdown(children=markdown_text),
        html.Div(id="days_ago", style=text_style),
        #className="p-5",
        slider,
        #check_box,
        html.Div(id="tab-content"),
        dbc.Tabs(
            id="tabs",
            active_tab="daily_tab",
            children=[
                dbc.Tab(
                    text_str,
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
        dbc.Button(
            "Refresh",
            color="primary",
            block=True,
            id="button_load_df",
            className="mb-3",
            href="/",
        ),
    ],
    fluid=True,
    style=style,
)


@app.callback(
    [Output("graph-all", "figure"),
     Output("graph-weekly", "figure"),
     Output("graph-heatmap-daily", "figure"),
     Output("graph-heatmap-weekly", "figure"),
     Output("days_ago", "children")],
    [Input("day-slider", "value")],
)
def updtae_plots(selected_time):
    df = get_frame_time_period(
        frame, window_start=int(selected_time)
    )
    column_groups = get_column_groups(df)    
    
    get_plots = [daily_figure, weekly_figure, make_a_daily_heatmap, make_a_weekly_heatmap]
    return *[f(df, column_groups) for f in get_plots], f" Time period: {int(selected_time) } days"


# @app.callback(Output("tab-content", "children"), [Input("tabs", "value")])
# def render_content(tab):
#     if tab == "tab-1":
#         return html.Div([html.H3("Tab content 1")])
#     elif tab == "tab-2":
#         return html.Div([html.H3("Tab content 2")])


if __name__ == "__main__":
    app.run_server(debug=True)
