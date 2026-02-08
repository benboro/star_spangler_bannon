# Star Spangler Bannon

A Python data analysis project that analyzes the timing of the National Anthem (The Star-Spangled Banner) by mapping lyrics to musical note lengths. Given a target duration, it calculates when each word should be sung.

Includes a baseball reference version that maps anthem words to MLB player names.

## Repository Structure

```
star_spangler_bannon/
├── data/
│   ├── bref_spangled_banner.csv    # Baseball reference lyrics mapping
│   ├── bref_word_length.csv        # Baseball reference word-to-note-length mapping
│   ├── score_anthem_data.csv       # Historical Super Bowl anthem performance times
│   ├── ssb_word_length.csv         # Word-to-note-length mapping (82 words)
│   └── star_spangled_banner.txt    # Full lyrics text
├── src/
│   ├── anthem_analysis.py          # CLI entry point
│   ├── anthem_utils.py             # Utility functions
│   └── web_app.py                  # Flask web interface
├── static/                         # Web interface static assets (CSS, JS)
├── templates/                      # Flask HTML templates
├── outputs/                        # Generated output files
├── .gitignore
├── CLAUDE.md
└── README.md
```

## Installation

```bash
pip install pandas xlsxwriter flask
```

## Usage

### CLI

Run from the project root directory:

```bash
# Default: 120.5s duration, standard lyrics, CSV output
python src/anthem_analysis.py

# Set a custom target duration (90 seconds)
python src/anthem_analysis.py -t 90

# Use baseball reference mode with a custom duration
python src/anthem_analysis.py --time 135.5 --bref

# Baseball reference mode + formatted Excel output
python src/anthem_analysis.py -t 100 -b -x
```

#### CLI Options

| Flag | Description |
|------|-------------|
| `-t`, `--time` | Target anthem duration in seconds (default: 120.5) |
| `-b`, `--bref` | Use baseball reference version (MLB player names) |
| `-x`, `--xlsx` | Export as formatted Excel instead of CSV |

### Web Interface

Start the Flask development server:

```bash
python src/web_app.py
```

Then open http://localhost:5000 in your browser. The web interface provides a karaoke-style lyric player that highlights words in real time based on the calculated timing.

The `/api/timing` endpoint returns JSON timing data and accepts these query parameters:

| Parameter | Description |
|-----------|-------------|
| `duration` | Target anthem duration in seconds (default: 120.5, clamped to 30–200) |
| `bref` | Set to `true` for baseball reference mode (default: `false`) |

## Output Files

Generated files are saved to the `outputs/` directory:

- `track_anthem_[TIME]s.csv` - Full data with all timing columns (default)
- `track_anthem_[TIME]s.xlsx` - Formatted Excel with Words and Time columns only (with `-x`)
- `_bref` suffix added when using baseball reference mode
