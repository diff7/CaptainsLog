import re
import gspread
import numpy as np
import pandas as pd
from omegaconf import OmegaConf as omg
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer


cfg = omg.load("./config.yaml")
PATH_TO_DATA = cfg.data_cvs
GSKEY = cfg.gskey


def pull_data_frame_from_google():
    gc = gspread.service_account()
    sh = gc.open_by_key(GSKEY)
    worksheet = sh.get_worksheet(0)
    dataframe = pd.DataFrame(worksheet.get_all_records())
    times_stamp = "Timestamp"
    dataframe[times_stamp] = pd.to_datetime(
        dataframe[times_stamp], format="%d/%m/%Y %H:%M:%S"
    )
    dataframe.set_index(times_stamp, inplace=True)
    dataframe.to_csv(PATH_TO_DATA)


def get_local_data_frame():
    dataframe = pd.read_csv(PATH_TO_DATA)
    times_stamp = "Timestamp"
    dataframe[times_stamp] = pd.to_datetime(
        dataframe[times_stamp], format="%Y/%m/%d %H:%M:%S"
    )
    dataframe.set_index(times_stamp, inplace=True)
    return dataframe


def get_column_groups(dataframe):
    column_tags = ["@text", "@textlist", "@time", "@scale", "@yesno"]
    column_groups = {k: [] for k in column_tags}
    for tag in column_tags:
        for col in dataframe.columns:
            if re.search(tag + "$", col):
                column_groups[tag].append(col)

    return column_groups


def processed_time(data):
    return data.apply(lambda x: x.dt.hour + x.dt.minute / 60, axis=1)


def digitize_data(last_week, column_groups):
    yes_no = process_yes_no_to_df(last_week[column_groups["@yesno"]])
    scale_cols = process_scale_cols_to_df(last_week[column_groups["@scale"]])
    time = processed_time(
        process_time_cols_to_df(last_week[column_groups["@time"]])
    )
    time_arr = np.where(time.values > 8, time.values, -time.values)
    time = pd.DataFrame(time_arr, columns=time.columns, index=time.index)
    out = pd.concat([yes_no, scale_cols, time], axis=1).fillna(0)
    out.rename(
        columns={col: filter_name(col) for col in out.columns}, inplace=True
    )
    return out


def get_frame_time_period(frame, window_start, window_end=0):
    end = datetime.now() - timedelta(days=window_end)
    start = datetime.now() - timedelta(days=window_start)
    return frame[(frame.index >= start) & (frame.index <= end)]


filter_name = lambda name: name.split("@")[0].capitalize()


def clean_word(string):
    return re.sub("[^A-Za-z0-9]+", " ", string)


def process_yes_no_to_df(yes_no_frame):
    yes_no_frame = yes_no_frame.apply(lambda x: x.str.lower(), axis=1)
    yes_no_frame = yes_no_frame.replace("yes", 1)
    yes_no_frame = yes_no_frame.replace("no", 0)
    yes_no_frame = yes_no_frame.replace("", 0)
    return yes_no_frame


def process_time_cols_to_df(time_frame):
    time_frame = time_frame.replace("", "00:00:00")
    time_frame.dropna(inplace=True)
    # time_frame = time_frame.apply(lambda x: '2016-01-01 ' + str(x), axis=1)
    time_frame = pd.concat(
        [
            pd.to_datetime(time_frame[col], format="%H:%M:%S")
            for col in time_frame.columns
        ],
        axis=1,
    )
    return time_frame


def mean_time(processed_time):
    return processed_time.apply(
        lambda x: x.mean().time().hour + x.mean().time().minute / 60, axis=0
    )


def process_scale_cols_to_df(scale_frame):
    return scale_frame


def get_last_text(text_frame, ago=-1):
    text_frame.fillna("-1", inplace=True)
    return {
        filter_name(k): v
        for k, v in text_frame.iloc[ago, :].to_dict().items()
        if v != "-1"
    }


def get_words_count_dict(text_df, min_size=3, max_w=250):
    text_df.fillna("-1", inplace=True)
    text_df = text_df.astype(str)
    lists_dict = text_df.to_dict(orient="list")

    out = dict()
    sentences = []
    for _, sent in lists_dict.items():
        for s in sent:
            s = clean_word(s.strip()).rstrip(" ").lower()
            sentences.append(s)

    vectorizer = TfidfVectorizer(
        max_df=0.99, min_df=0.01, stop_words="english", max_features=max_w
    )
    vectorizer.fit(sentences)
    filtered_words = vectorizer.get_feature_names()
    filtered_words = [w for w in filtered_words if len(w) > min_size]

    for k, sent in lists_dict.items():
        words_count = dict()
        for s in sent:
            s = clean_word(s.strip()).rstrip(" ").lower()
            for w in s.split(" "):
                if w in filtered_words:
                    if len(w) > min_size:
                        if w in words_count:
                            words_count[w] += 1
                        else:
                            words_count[w] = 1

        out[filter_name(k)] = words_count
    return out, sentences


def mean_report_dict(last_week, column_groups):
    yes_no = (
        process_yes_no_to_df(last_week[column_groups["@yesno"]])
        .sum(0)
        .to_dict()
    )
    yes_no = {filter_name(k): v for k, v in yes_no.items()}

    scale_cols = (
        process_scale_cols_to_df(last_week[column_groups["@scale"]])
        .mean(0)
        .to_dict()
    )
    scale_cols = {filter_name(k): v for k, v in scale_cols.items()}

    mean_t = mean_time(
        process_time_cols_to_df(last_week[column_groups["@time"]])
    ).to_dict()
    mean_t = {filter_name(k): v for k, v in mean_t.items()}

    return {"yes_no": yes_no, "scale_cols": scale_cols, "mean_t": mean_t}


def mean_report_df(last_week, column_groups):
    data = digitize_data(last_week, column_groups)
    data["week"] = data.index.week
    return data.groupby("week").mean(0)


def init_data(period):
    frame = get_local_data_frame()
    frame = get_frame_time_period(frame, window_start=period)
    column_groups = get_column_groups(frame)
    return frame, column_groups


def make_weekly_stats(data_frame, column_groups):
    weeks = int(data_frame.shape[1] / 7)
    mean_weeks = []
    for i in range(weeks - 1, -1, -1):
        week = get_frame_time_period(
            data_frame, window_start=(i + 1) * 7, window_end=i * 7
        )
        mean_weeks.append(mean_report_dict(week, column_groups))

    mean_weeks_dict = {}
    for mean_week in mean_weeks:
        for tp in mean_week:
            for key in mean_week[tp]:
                if not key in mean_weeks_dict:
                    mean_weeks_dict[key] = []
                mean_weeks_dict[key].append(mean_week[tp][key])

    return mean_weeks_dict, weeks