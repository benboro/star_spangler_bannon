import os
import re
import sys
import json

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


def get_bref_karaoke_lines():
    """Read bref_spangled_banner.txt and return karaoke lines."""
    path = os.path.join(DATA_DIR, "bref_spangled_banner.txt")
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f]

    return [line for line in lines if line]


def get_bref_links():
    """Read bref_spangled_banner.json and return ordered Baseball Reference links."""
    path = os.path.join(DATA_DIR, "bref_spangled_banner.json")
    with open(path, "r", encoding="utf-8") as f:
        entries = json.load(f)
    return [entry.get("bref_link") for entry in entries]


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


def build_bref_lines(df, bref_karaoke_lines, bref_links):
    """Group BREF dataframe rows into lines based on karaoke lines in bref_spangled_banner.txt."""
    df_filtered = df[df["words"] != "[end]"].copy()
    if len(bref_links) < len(df_filtered):
        raise ValueError("bref link data has fewer entries than timing words")

    lines = []
    idx = 0
    for line_text in bref_karaoke_lines:
        target = " ".join(line_text.split())
        line_words = []
        assembled = []
        matched = False

        while idx < len(df_filtered):
            row = df_filtered.iloc[idx]
            line_words.append({
                "word": row["words"],
                "startTime": round(row["word_start_time"], 4),
                "endTime": round(row["word_cum_time"], 4),
                "duration": round(row["word_time"], 4),
                "link": bref_links[idx] if idx < len(bref_links) else None,
            })
            assembled.append(row["words"])
            idx += 1

            candidate = " ".join(assembled)
            if candidate == target:
                matched = True
                break

        if line_words and not matched:
            raise ValueError(
                "bref_spangled_banner.txt line does not align with timing data: '{}'".format(target)
            )
        if line_words:
            lines.append({"words": line_words})

    # Keep any trailing words if the text file line counts are ever short.
    if idx < len(df_filtered):
        trailing_words = []
        while idx < len(df_filtered):
            row = df_filtered.iloc[idx]
            trailing_words.append({
                "word": row["words"],
                "startTime": round(row["word_start_time"], 4),
                "endTime": round(row["word_cum_time"], 4),
                "duration": round(row["word_time"], 4),
                "link": bref_links[idx] if idx < len(bref_links) else None,
            })
            idx += 1
        lines.append({"words": trailing_words})

    return lines


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/timing")
def timing():
    duration = request.args.get("duration", 119.5, type=float)
    bref = request.args.get("bref", "false").lower() == "true"

    # clamp duration
    duration = max(30, min(200, duration))

    # read and compute timing using existing utilities
    filename = "bref_word_length.json" if bref else "ssb_word_length.json"

    df = aut.read_lyric_data(path=os.path.join(DATA_DIR, filename))
    df = aut.create_time_columns(df=df, song_duration=duration)

    if bref:
        bref_karaoke_lines = get_bref_karaoke_lines()
        bref_links = get_bref_links()
        lines = build_bref_lines(df, bref_karaoke_lines, bref_links)
    else:
        line_word_counts = get_ssb_line_word_counts()
        lines = build_ssb_lines(df, line_word_counts)

    return jsonify({
        "duration": duration,
        "bref": bref,
        "lines": lines,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
