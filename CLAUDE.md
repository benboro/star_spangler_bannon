# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Star Spangler Bannon is a Python data analysis project that analyzes the timing of the National Anthem (The Star-Spangled Banner) by mapping lyrics to musical note lengths. Given a target duration, it calculates when each word should be sung.

The project includes a baseball reference version that maps anthem words to MLB player names.

## Commands

**Run the analysis:**
```bash
python anthem_analysis.py
```

This generates timing analysis files in `outputs/` for the target duration (currently 120.5 seconds).

**Dependencies:**
```bash
pip install pandas xlsxwriter
```

## Architecture

### Core Files

- **anthem_analysis.py** - Entry point. Loads Super Bowl anthem timing data, sets target duration, calls `run_lyrics_analysis()`
- **anthem_utils.py** - All utility functions for time conversion, lyrics processing, data analysis, and export

### Data Files

- **ssb_word_length.csv** - Word-to-note-length mapping (82 words from first stanza)
- **bref_word_length.csv** - Baseball Reference version with MLB player names
- **score_anthem_data.csv** - Historical Super Bowl anthem performance times

### Key Functions in anthem_utils.py

- `run_lyrics_analysis(song_duration, directory, bref, all_cols)` - Main pipeline orchestrator
- `create_time_columns(df, song_duration)` - Calculates timing metrics (note_share, word_time, word_cum_time, word_start_time)
- `export_data(df, path_directory, song_duration, bool_bref, all_cols)` - Exports to CSV or formatted Excel
- `read_lyric_data(path, encode, bool_bref)` - Loads and validates CSV data
- `minutes_to_seconds(time_val)` / `seconds_to_minutes(total_seconds)` - Time format conversion

### Output

Generated files go to `outputs/`:
- `track_anthem_[TIME]s.csv` - Full data with all timing columns
- `track_anthem_[TIME]s.xlsx` - Formatted Excel with Words and Time columns only

## Encoding Notes

- Star-Spangled Banner text: UTF-8
- Internal data files and exports: cp1252
