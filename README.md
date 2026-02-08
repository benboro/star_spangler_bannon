# Star Spangler Bannon

Star Spangler Bannon analyzes National Anthem timing by mapping each word to note length and distributing timing to match a target duration.

It includes:
- Standard Star-Spangled Banner timing
- Baseball Reference mode (anthem words replaced with MLB player names)
- A Flask karaoke-style player UI

## Installation

```bash
pip install pandas xlsxwriter flask
```

## Repository Structure

```text
star_spangler_bannon/
|-- data/         # Input data (JSON default, CSV legacy, lyrics text files)
|-- src/          # Python source (CLI + Flask app + export script)
|-- static/       # CSS/JS for web player
|-- templates/    # HTML templates for Flask
|-- outputs/      # Generated analysis files (gitignored)
|-- CLAUDE.md
|-- AGENTS.md
`-- README.md
```

## Usage

### CLI

Run from project root:

```bash
# Default: 119.5 seconds, standard lyrics, JSON output
python src/anthem_analysis.py

# Custom duration
python src/anthem_analysis.py -t 90

# Baseball Reference mode
python src/anthem_analysis.py --time 135.5 --bref

# CSV input/output compatibility mode
python src/anthem_analysis.py --csv

# Excel output
python src/anthem_analysis.py -t 100 -b -x
```

CLI flags:

| Flag | Description |
|------|-------------|
| `-t`, `--time` | Target duration in seconds (default `119.5`) |
| `-b`, `--bref` | Baseball Reference mode |
| `-x`, `--xlsx` | Export formatted Excel output |
| `-c`, `--csv` | Use legacy CSV input/output paths |

### Web App

Start Flask:

```bash
python src/web_app.py
```

Open `http://localhost:5000`.

Current player behavior:
- Default duration is `119.5`.
- Duration can be changed with slider or numeric input.
- Duration resolves to nearest `0.5` second and is clamped to `30-200`.
- Top-left "Return to borovinsky.com" button is available on setup and karaoke screens.
- Karaoke mode keeps sung words highlighted.
- Baseball Reference mode switches title to "Star Spangler Bannon Tracker".
- Baseball Reference karaoke names are clickable and open Baseball Reference pages.
- On mobile karaoke view, lyrics scroll inside the lyrics container so controls/progress stay accessible.

API endpoint:

`GET /api/timing`

| Parameter | Description |
|-----------|-------------|
| `duration` | Target duration in seconds (default `119.5`, server clamps `30-200`) |
| `bref` | `true` for Baseball Reference mode, otherwise `false` |

## Data Files

Important files in `data/`:
- `ssb_word_length.json` - Standard word-to-note mapping
- `bref_word_length.json` - Baseball Reference word-to-note mapping
- `star_spangled_banner.txt` - Standard lyrics source text
- `bref_spangled_banner.txt` - Baseball Reference karaoke line breaks/layout
- `bref_spangled_banner.json` - Baseball Reference metadata, including per-word links
- `score_anthem_data.json` - Historical anthem performance timing data

Legacy CSV equivalents are also present for backward compatibility.

## Output Files

Generated files are written to `outputs/`:
- `track_anthem_[TIME]s.json` (default)
- `track_anthem_[TIME]s.csv` (with `--csv`)
- `track_anthem_[TIME]s.xlsx` (with `--xlsx`)
- `_bref` suffix is added when Baseball Reference mode is used

## Cross-Repo Sync (benboro.github.io)

This repo is the Flask/dev version. The production static player lives in:

`C:\Projects\website\ssb-player\`

After UI/data updates are verified locally, sync these files:
- `static/css/style.css` -> `C:\Projects\website\ssb-player\style.css`
- `templates/index.html` -> `C:\Projects\website\ssb-player\index.html`
- `static/js/player.js` -> `C:\Projects\website\ssb-player\player.js`

For HTML sync, replace Flask static refs:
- `{{ url_for('static', filename='css/style.css') }}` -> `style.css`
- `{{ url_for('static', filename='js/player.js') }}` -> `player.js`

If timing source data changes (`data/ssb_word_length.json` or `data/bref_word_length.json`):

```bash
python src/export_js_data.py
```

Then paste regenerated data into the top data block in static `player.js`.
