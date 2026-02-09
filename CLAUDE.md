# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Star Spangler Bannon is a Python data analysis project that analyzes the timing of the National Anthem (The Star-Spangled Banner) by mapping lyrics to musical note lengths. Given a target duration, it calculates when each word should be sung.

The project includes a baseball reference version that maps anthem words to MLB player names.

## Commands

**Run the analysis:**
```bash
python src/anthem_analysis.py
python src/anthem_analysis.py -t 90 -b    # 90 seconds, baseball reference mode
python src/anthem_analysis.py -x           # Excel output instead of CSV
```

**Run the web interface:**
```bash
python src/web_app.py                      # opens at http://localhost:5000
```

**Dependencies:**
```bash
pip install pandas xlsxwriter flask
```

## Architecture

### Directory Structure

```
star_spangler_bannon/
├── data/           # Input data files (JSON default, CSV legacy, lyrics text)
├── docs/           # Writeup (Rmd/HTML) and image assets
├── src/            # Python source files
├── static/         # Web interface static assets (CSS, JS)
├── templates/      # Flask HTML templates
├── outputs/        # Generated output files (gitignored)
├── .gitignore
├── CLAUDE.md
└── README.md
```

### Core Files

- **src/anthem_analysis.py** - CLI entry point with argparse. Supports `-t`/`--time`, `-b`/`--bref`, `-x`/`--xlsx`, `-c`/`--csv` flags
- **src/anthem_utils.py** - All utility functions for time conversion, lyrics processing, data analysis, and export
- **src/web_app.py** - Flask web interface with karaoke-style lyric player. Reuses `anthem_utils` for timing calculations

### Data Files (in `data/`)

- **ssb_word_length.json** - Word-to-note-length mapping (JSON, default)
- **bref_word_length.json** - Baseball Reference version with MLB player names (JSON, default)
- **score_anthem_data.json** - Historical Super Bowl anthem performance times
- **bref_spangled_banner.json** - Baseball reference lyrics mapping
- **star_spangled_banner.txt** - Full lyrics text
- **\*.csv** - Legacy CSV versions of the above (used with `--csv` flag)

### Key Functions in src/anthem_utils.py

- `run_lyrics_analysis(song_duration, data_dir, output_dir, bref, all_cols, use_csv)` - Main pipeline orchestrator
- `create_time_columns(df, song_duration)` - Calculates timing metrics (note_share, word_time, word_cum_time, word_start_time)
- `export_data(df, output_dir, song_duration, bool_bref, all_cols, use_csv)` - Exports to JSON, CSV, or formatted Excel
- `read_lyric_data(path, encode, bool_bref)` - Loads and validates data from JSON or CSV
- `minutes_to_seconds(time_val)` / `seconds_to_minutes(total_seconds)` - Time format conversion

### Output

Generated files go to `outputs/`:
- `track_anthem_[TIME]s.json` - Full data with all timing columns (default)
- `track_anthem_[TIME]s.csv` - Full data with all timing columns (with `--csv`)
- `track_anthem_[TIME]s.xlsx` - Formatted Excel with Words and Time columns only

## Encoding Notes

- JSON data files: UTF-8 (eliminates legacy encoding complexity)
- Star-Spangled Banner text: UTF-8
- Legacy CSV data files and CSV exports: cp1252
