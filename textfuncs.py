import dash_core_components as dcc
import dash_html_components as html
from main import get_last_text


def get_last_text_records(frame, column_groups, ago):
    text = ["DATE: " + str(frame.reset_index().iloc[ago, 0])]
    last_text = get_last_text(frame[column_groups["@text"]], ago)
    for col in last_text:
        t = last_text[col]
        if len(t) > 2:
            text.append("\n * *" + col.upper() + "*")
            if len(t.split("\n")) > 2:
                # text.append("\n > -")
                text.append(
                    "".join(["\n> " + s for s in t.split("\n") if len(s) > 2])
                )
            else:
                text.append("\n> " + t)
    return dcc.Markdown(
        " ".join(text), style={"width": "100%", "max-width": "500px"}
    )


# def get_last_text_records(frame, column_groups, ago):
#     text = ["DATE: " + str(frame.reset_index().iloc[ago, 0])]
#     last_text = get_last_text(frame[column_groups["@text"]], ago)
#     for col in last_text:
#         t = last_text[col]
#         if len(t) > 2:
#             text.append(html.P(col.upper()))
#             if len(t.split("\n")) > 2:
#                 # text.append("\n > -")
#                 text.append([html.P(s) for s in t.split("\n") if len(s) > 2])
#             else:
#                 text.append(html.P(t))
#     return html.Div(children=text)
