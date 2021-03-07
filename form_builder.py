from omegaconf import OmegaConf as omg
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from styles import text_style

from basic_writer import write


def text_area_form(question, s_range=None, app=None):
    form_id = "_".join(question.lower().split(" "))
    main_input = dbc.FormGroup(
        [
            dbc.Label(question, html_for="entry-form"),
            dbc.Textarea(
                # type="question",
                id=form_id,
                value="Your cool thoughts come here ...",
                style={"height": 50},
            ),
            dbc.FormText(
                "Use #tags for specific words",
                color="secondary",
            ),
        ]
    )

    return main_input


def make_slider(question, s_range=None, app=None):
    if s_range is None:
        s_range = 5
    slider_id = "_".join(question.lower().split(" "))
    slider_label = slider_id + "_label"
    slider = dcc.Slider(
        id=slider_id, min=min(s_range), max=max(s_range), value=1
    )

    @app.callback(Output(slider_label, "children"), Input(slider_id, "value"))
    def set_slider_value(value):
        if value is None:
            value = 1
        return f"Seleceted value: {int(value) } days"

    return html.Div([html.Div(id=slider_label, style=text_style), slider])


type_to_method = {"textarea": text_area_form, "scale": make_slider}


def build_forms(app, sql_connect):
    button_id = "button_forms_all"

    forms = omg.cfg = omg.load("./config.yaml").forms
    assert (
        forms is not None
    ), "No forms were provided to the builder, check config"

    new_forms = []
    form_ids = []
    inputs = []
    if len(forms) > 0:
        for item in forms:
            if item.type in type_to_method:
                form_ids.append("_".join(item.question.lower().split(" ")))
                print(item.question)
                new_forms.append(
                    type_to_method[item.type](item.question, item.s_range, app)
                )

    new_forms.append(
        dbc.Button("Submit", id=button_id, color="primary", n_clicks=0)
    )

    @app.callback(
        [Output(form_id, "value") for form_id in form_ids],
        Input(button_id, "n_clicks"),
        [State(form_id, "value") for form_id in form_ids],
    )
    def update_output(n_clicks, *values):
        out = []
        if n_clicks == 0:
            return values

        for v, q in zip(values, form_ids):
            print(v, q)
            write(sql_connect, str(v), q)
            out.append(v)
        return out

    return html.Div(new_forms)
