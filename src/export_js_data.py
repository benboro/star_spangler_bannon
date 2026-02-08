"""Export JSON data as JavaScript constants for the static GitHub Pages player.

Usage:
    python src/export_js_data.py

Prints JavaScript variable declarations to stdout. Redirect to a file or
copy-paste into player.js if the source data files are ever updated.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

sys.path.insert(0, SCRIPT_DIR)
import anthem_utils as aut


def js_string(s):
    """Escape a string for use in a JavaScript source literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def export_data_array(name, df):
    """Print a JS array of {word, noteLength} from a lyrics dataframe."""
    print("    var {} = [".format(name))
    rows = []
    for _, row in df.iterrows():
        word = row["words"]
        if word == "[end]":
            continue
        note = row["note_length"]
        rows.append('        {{word: "{}", noteLength: {}}}'.format(js_string(word), note))
    print(",\n".join(rows))
    print("    ];")


def export_line_word_counts():
    """Print LINE_WORD_COUNTS from star_spangled_banner.txt first stanza."""
    path = os.path.join(DATA_DIR, "star_spangled_banner.txt")
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f]

    stanza_lines = []
    for line in lines:
        if len(line):
            stanza_lines.append(line)
        else:
            break

    counts = [len(line.split()) for line in stanza_lines]
    print("    var LINE_WORD_COUNTS = [{}];".format(", ".join(str(c) for c in counts)))


def main():
    ssb_df = aut.read_lyric_data(
        path=os.path.join(DATA_DIR, "ssb_word_length.json")
    )
    bref_df = aut.read_lyric_data(
        path=os.path.join(DATA_DIR, "bref_word_length.json")
    )

    print("    // Auto-generated from JSON data. Do not edit manually.")
    print()
    export_data_array("SSB_DATA", ssb_df)
    print()
    export_data_array("BREF_DATA", bref_df)
    print()
    export_line_word_counts()


if __name__ == "__main__":
    main()
