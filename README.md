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

## Web UI Development Workflow

The web interface exists in two forms:

1. **Flask app** (this repo) — `static/`, `templates/`, `src/web_app.py`. Uses a server-side `/api/timing` endpoint.
2. **Static GitHub Pages player** — `C:\Projects\website\ssb-player\` (the [benboro.github.io](https://github.com/benboro/benboro.github.io) repo). All timing computation runs client-side in `player.js`.

### Debugging locally

Use the Flask app for development since it picks up file changes without a build step:

```bash
python src/web_app.py
# open http://localhost:5000
```

Edit `static/js/player.js` and `static/css/style.css` directly — refresh the browser to see changes.

### Updating the GitHub Pages player

After changes are working in the Flask app, sync them to the static player:

1. **CSS changes** — copy `static/css/style.css` directly to `C:\Projects\website\ssb-player\style.css`.
2. **HTML changes** — copy `templates/index.html` to `C:\Projects\website\ssb-player\index.html`, then replace the two `{{ url_for(...) }}` calls with relative paths (`style.css` and `player.js`).
3. **JS changes** — the static `player.js` has the same UI code but replaces the `fetch("/api/timing")` call with local computation functions and embedded data arrays. Copy your UI changes into the corresponding section of `C:\Projects\website\ssb-player\player.js`, keeping the data/computation block at the top intact.
4. **CSV data changes** — if `data/ssb_word_length.csv` or `data/bref_word_length.csv` change, regenerate the embedded JS data:
   ```bash
   python src/export_js_data.py
   ```
   Then paste the output into the data section at the top of the static `player.js`.

### Publishing

```bash
cd C:\Projects\website
git add ssb-player/
git commit -m "Update SSB player"
git push
```

The player is live at https://borovinsky.com/ssb-player/ once GitHub Pages deploys (usually under a minute).

## Output Files

Generated files are saved to the `outputs/` directory:

- `track_anthem_[TIME]s.csv` - Full data with all timing columns (default)
- `track_anthem_[TIME]s.xlsx` - Formatted Excel with Words and Time columns only (with `-x`)
- `_bref` suffix added when using baseball reference mode
