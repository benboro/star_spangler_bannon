# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project Overview

Star Spangler Bannon is a Python data analysis project that analyzes the timing of the National Anthem (The Star-Spangled Banner) by mapping lyrics to musical note lengths. Given a target duration, it calculates when each word should be sung.

The project includes a baseball reference version that maps anthem words to MLB player names.

## Commands

Run the analysis:
```bash
python src/anthem_analysis.py
python src/anthem_analysis.py -t 90 -b
python src/anthem_analysis.py -x
```

Run the web interface:
```bash
python src/web_app.py
```

Dependencies:
```bash
pip install pandas xlsxwriter flask
```

## Architecture

### Directory Structure

```text
star_spangler_bannon/
|-- data/        # Input data files (JSON default, CSV legacy, lyrics text)
|-- src/         # Python source files
|-- static/      # Web interface static assets (CSS, JS)
|-- templates/   # Flask HTML templates
|-- outputs/     # Generated output files (gitignored)
|-- .gitignore
|-- CLAUDE.md
|-- AGENTS.md
`-- README.md
```

### Core Files

- `src/anthem_analysis.py` - CLI entry point with argparse. Supports `-t`/`--time`, `-b`/`--bref`, `-x`/`--xlsx`, `-c`/`--csv`.
- `src/anthem_utils.py` - Utility functions for time conversion, lyrics processing, timing analysis, and export.
- `src/web_app.py` - Flask web interface with karaoke-style lyric player. Reuses `anthem_utils` for timing calculations.
- `src/export_js_data.py` - Generates JS-friendly data blobs for the static player in `benboro.github.io`.

### Data Files (in `data/`)

- `ssb_word_length.json` - Word-to-note-length mapping (JSON default)
- `bref_word_length.json` - Baseball reference version with MLB player names (JSON default)
- `score_anthem_data.json` - Historical Super Bowl anthem performance times
- `bref_spangled_banner.json` - Baseball reference lyrics mapping
- `star_spangled_banner.txt` - Full lyrics text
- `*.csv` - Legacy CSV versions (used with `--csv`)

### Key Functions in `src/anthem_utils.py`

- `run_lyrics_analysis(song_duration, data_dir, output_dir, bref, all_cols, use_csv)` - Main analysis pipeline.
- `create_time_columns(df, song_duration)` - Calculates timing metrics (`note_share`, `word_time`, `word_cum_time`, `word_start_time`).
- `export_data(df, output_dir, song_duration, bool_bref, all_cols, use_csv)` - Exports JSON, CSV, or formatted Excel.
- `read_lyric_data(path, encode, bool_bref)` - Loads and validates JSON or CSV data.
- `minutes_to_seconds(time_val)` / `seconds_to_minutes(total_seconds)` - Time format conversion helpers.

### Output

Generated files are written to `outputs/`:
- `track_anthem_[TIME]s.json` (default)
- `track_anthem_[TIME]s.csv` (with `--csv`)
- `track_anthem_[TIME]s.xlsx` (with `--xlsx`)
- `_bref` suffix is added when using baseball reference mode

## Encoding Notes

- JSON data files: UTF-8
- `star_spangled_banner.txt`: UTF-8
- Legacy CSV files and CSV exports: cp1252

## Cross-Repo Sync: benboro.github.io

This repo contains the Flask/dev version of the SSB player. The production static player lives in the `benboro.github.io` repo at:

- `C:\Projects\website\ssb-player\`

When UI or data logic changes here, update the corresponding static files there:

1. CSS mapping:
- `static/css/style.css` -> `C:\Projects\website\ssb-player\style.css`

2. HTML mapping:
- `templates/index.html` -> `C:\Projects\website\ssb-player\index.html`
- Replace Flask template refs:
  - `{{ url_for('static', filename='css/style.css') }}` -> `style.css`
  - `{{ url_for('static', filename='js/player.js') }}` -> `player.js`

3. JavaScript mapping:
- `static/js/player.js` -> `C:\Projects\website\ssb-player\player.js`
- Keep the static player's local data/computation block intact (no `/api/timing` fetch); port only shared UI behavior changes unless intentionally changing static computation logic.

4. Data updates for static player:
- If `data/ssb_word_length.json` or `data/bref_word_length.json` changes, regenerate JS data:
```bash
python src/export_js_data.py
```
- Paste regenerated arrays/objects into the data section at the top of `C:\Projects\website\ssb-player\player.js`.

## Recommended Workflow

1. Make and verify changes locally via Flask (`python src/web_app.py`).
2. Sync mapped files to `C:\Projects\website\ssb-player\`.
3. If data changed, run `python src/export_js_data.py` and update static `player.js` data.
4. Commit and push changes in each repo as needed.
