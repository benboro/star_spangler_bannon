import os
import re
import sys

from flask import Flask, jsonify, render_template, request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

sys.path.insert(0, SCRIPT_DIR)
import anthem_utils as aut

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
)


def get_ssb_line_word_counts():
    """Read first stanza of star_spangled_banner.txt and return word counts per line."""
    path = os.path.join(DATA_DIR, "star_spangled_banner.txt")
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f]

    # first stanza only (up to first blank line)
    stanza_lines = []
    for line in lines:
        if len(line):
            stanza_lines.append(line)
        else:
            break

    # count words per line
    counts = []
    for line in stanza_lines:
        words = line.split()
        counts.append(len(words))

    return counts


def build_ssb_lines(df, line_word_counts):
    """Group SSB dataframe rows into lines based on word counts from lyrics text."""
    lines = []
    idx = 0
    for count in line_word_counts:
        line_words = []
        for _ in range(count):
            if idx >= len(df):
                break
            row = df.iloc[idx]
            word = row["words"]
            if word == "[end]":
                idx += 1
                continue
            line_words.append({
                "word": word,
                "startTime": round(row["word_start_time"], 4),
                "endTime": round(row["word_cum_time"], 4),
                "duration": round(row["word_time"], 4),
            })
            idx += 1
        if line_words:
            lines.append({"words": line_words})
    return lines


def build_bref_lines(df, ssb_line_word_counts):
    """Group BREF dataframe rows into lines using cumulative note_length share thresholds."""
    # compute SSB cumulative word count boundaries as share of total words
    ssb_total = sum(ssb_line_word_counts)
    ssb_cum = []
    running = 0
    for count in ssb_line_word_counts:
        running += count
        ssb_cum.append(running / ssb_total)

    # filter out [end] row
    df_filtered = df[df["words"] != "[end]"].copy()

    # compute cumulative note_length share for each BREF entry
    total_note_length = df_filtered["note_length"].sum()
    df_filtered = df_filtered.copy()
    df_filtered["cum_share"] = df_filtered["note_length"].cumsum() / total_note_length

    # assign each word to a line based on where its cumulative share falls
    lines = [[] for _ in ssb_line_word_counts]
    for _, row in df_filtered.iterrows():
        cum = row["cum_share"]
        line_idx = 0
        for i, threshold in enumerate(ssb_cum):
            if cum <= threshold + 1e-9:
                line_idx = i
                break
        else:
            line_idx = len(ssb_cum) - 1

        lines[line_idx].append({
            "word": row["words"],
            "startTime": round(row["word_start_time"], 4),
            "endTime": round(row["word_cum_time"], 4),
            "duration": round(row["word_time"], 4),
        })

    return [{"words": line} for line in lines if line]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/timing")
def timing():
    duration = request.args.get("duration", 120.5, type=float)
    bref = request.args.get("bref", "false").lower() == "true"

    # clamp duration
    duration = max(30, min(200, duration))

    # read and compute timing using existing utilities
    filename = "bref_word_length.json" if bref else "ssb_word_length.json"

    df = aut.read_lyric_data(path=os.path.join(DATA_DIR, filename))
    df = aut.create_time_columns(df=df, song_duration=duration)

    # get SSB line word counts for line grouping
    line_word_counts = get_ssb_line_word_counts()

    if bref:
        lines = build_bref_lines(df, line_word_counts)
    else:
        lines = build_ssb_lines(df, line_word_counts)

    return jsonify({
        "duration": duration,
        "bref": bref,
        "lines": lines,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
