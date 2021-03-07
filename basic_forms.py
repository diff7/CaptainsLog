from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from basic_writer import write, SqlConnect


def make_one_question_form(app, sql_connect):
    main_input = dbc.FormGroup(
        [
            dbc.Label("Write here", html_for="entry-form"),
            dbc.Textarea(
                # type="question",
                id="question-form",
                value="Your cool thoughts come here ...",
                style={"height": 300},
            ),
            dbc.FormText(
                "Use #tags for specific words",
                color="secondary",
            ),
        ]
    )

    form = dbc.Form(
        [
            main_input,
            dbc.Button(
                "Submit", id="question-button", color="primary", n_clicks=0
            ),
        ],
    )

    @app.callback(
        Output("question-form", "value"),
        Input("question-button", "n_clicks"),
        State("question-form", "value"),
    )
    def update_output(n_clicks, value):
        if n_clicks > 0:
            write(sql_connect, value)

            return "You have entered: \n{}".format(value)

    return form


# form_block  = html.Div([
#     dcc.Textarea(
#         id='question',
#         value="Your cool thoughts come here ...",
#         style={'width': '100%', 'height': 200},
#     ),
#     html.Button('Submit', id='question-button', n_clicks=0),
#     html.Div(id='question-output', style={'whiteSpace': 'pre-line'})
#     ])

# @app.callback(
#     Output('textarea-state-example-output', 'children'),
#     Input('textarea-state-example-button', 'n_clicks'),
#     State('textarea-state-example', 'value')
# )
# def update_output(n_clicks, value):
#     if n_clicks > 0:
#         return 'You have entered: \n{}'.format(value)
