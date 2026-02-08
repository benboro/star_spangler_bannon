import argparse
import os

import anthem_utils as aut

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Star-Spangled Banner timing by mapping lyrics to note lengths"
    )
    parser.add_argument("-t", "--time", type=float, default=120.5,
                        metavar="SECONDS",
                        help="Target anthem duration in seconds (default: 120.5)")
    parser.add_argument("-b", "--bref", action="store_true",
                        help="Use baseball reference version (MLB player names)")
    parser.add_argument("-x", "--xlsx", action="store_true",
                        help="Export as formatted Excel instead of JSON")
    parser.add_argument("-c", "--csv", action="store_true",
                        help="Use CSV format for input/output instead of JSON (default)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    aut.run_lyrics_analysis(
        song_duration=args.time,
        data_dir=DATA_DIR,
        output_dir=OUTPUT_DIR,
        bref=args.bref,
        all_cols=not args.xlsx,
        use_csv=args.csv
    )


if __name__ == "__main__":
    main()
