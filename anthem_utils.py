import os
import re
from typing import Union

import pandas as pd
import xlsxwriter


def minutes_to_seconds(time_val: str) -> int:
    """Converts time in %M:%S string format to seconds represented as an integer"""
    splt = time_val.split(":")
    minutes = int(splt[0])
    seconds = int(splt[1])
    total_seconds = minutes * 60 + seconds

    return total_seconds


def seconds_to_minutes(total_seconds: Union[int, float], prec: int = 1) -> str:
    """Converts seconds to time in %M:%S string format"""
    minutes = int(total_seconds / 60)
    seconds = total_seconds % 60
    nlen = 3 + prec
    time_val = "{m}:{s:0{num_len}.{precision}f}".format(m=minutes, s=seconds, num_len=nlen, precision=prec)

    return time_val


def read_ssb_lyrics(path: str) -> list:
    """Reads lyrics from text file and returns lyrics as list of words"""
    # read text file containing lyrics to Star Spangled Banner
    with open(path, 'r', encoding='utf-8') as file:
        ssb_lines_full = [ln.strip() for ln in file]

    # our national anthem uses only the first stanza
    ssb_lines_anthem = []
    for line in ssb_lines_full:
        if len(line):
            ssb_lines_anthem += [line]
        else:
            break

    # pull words from lines
    ssb_words = ('\n'.join(ssb_lines_anthem)).split()

    # remove non-word characters at the end of words
    ssb_words = [re.sub(r"\W$", "", w) for w in ssb_words]

    return ssb_words


def ssb_lyrics_to_dataframe(path_directory, output_filename="ssb_words.csv"):
    """Get lyrics in Star Spangled Banner as list of words"""
    ssb_words = read_ssb_lyrics(path=os.path.join(path_directory, "star_spangled_banner.txt"))
    pd.DataFrame({"words": ssb_words}) \
        .to_csv(os.path.join(path_directory, output_filename), index=False, encoding="cp1252")


def read_lyric_data(path: str, encode: str = None, bool_bref: bool = False) -> pd.DataFrame:
    """Reads lyric data from csv file and returns dataframe"""
    # note lengths manually calculated using sheet music from https://hymnary.org/media/fetch/147497
    if encode is None:
        encode = "utf-8" if bool_bref else "cp1252"
    lyric_data = pd.read_csv(path, encoding=encode)
    if lyric_data['note_length'].dtype != float:
        raise Exception("Make sure every word has a corresponding note length in the csv file")

    return lyric_data


def create_time_columns(df: pd.DataFrame, song_duration: Union[int, float]) -> pd.DataFrame:
    """Adds columns to dataframes for time computation/analysis"""

    # get share of how long each note is relative to the whole song
    notes_sum = sum(df['note_length'])
    df['note_share'] = df.apply(lambda x: x['note_length'] / notes_sum, axis=1)

    # multiply time to note share to get how long each word is in seconds
    df['word_time'] = df.apply(lambda x: x['note_share'] * song_duration, axis=1)

    # add fields that track progress of each word through song
    df['word_cum_time'] = df['word_time'].cumsum()
    df['word_start_time'] = df['word_cum_time'].shift(1, fill_value=0)
    df['format_start_time'] = df.apply(lambda x: seconds_to_minutes(x['word_start_time']), axis=1)

    return df


def export_data(
        df: pd.DataFrame,
        path_directory: str,
        song_duration: Union[int, float],
        bool_bref: bool = False):
    """Exports dataframe to csv"""

    # export only necessary fields (and rename them)
    cols_to_rename = {"words": "Words", "format_start_time": "Time"}
    export_df = df[cols_to_rename.keys()].rename(columns=cols_to_rename)
    export_filename = "track_anthem_{tm}s{suf}.xlsx".format(tm=str(song_duration), suf=("_bref" if bool_bref else ""))
    export_fullpath = os.path.join(path_directory, "outputs", export_filename)

    align_left = {'align': 'left'}
    bold_true = {'bold': True}
    color_black = '#000000'
    top_border = {'top': 1, 'top_color': color_black}
    bottom_border = {'bottom': 1, 'bottom_color': color_black}
    excel_options = {
        "default_date_format": "yyyy-mm-dd",
        "default_format_properties": {"font_name": "Calibri", "font_size": 11, 'bg_color': '#FFFFFF'}
    }
    with xlsxwriter.Workbook(filename=export_fullpath, options=excel_options) as wb:
        ws = wb.add_worksheet(name="Lyrics")
        row_start = 1
        col_start = 1

        fmt_header_left = wb.add_format({**bold_true, **align_left, **top_border, **bottom_border})

        row_current = row_start
        col_current = col_start

        # write columns to worksheet
        for ic, colname in enumerate(export_df.columns):
            ws.write_string(row_current, col_current + ic, colname, cell_format=fmt_header_left)

        # write values to worksheet
        for row_df in range(len(export_df)):
            row_current += 1

            fmt_master = {}
            bool_lastrow = row_df == len(export_df) - 1

            for ir, (fld, value) in enumerate(export_df.iloc[row_df].to_dict().items()):
                fmt_list = []
                bool_blank = pd.isna(value)

                if bool_lastrow:
                    fmt_list.append(bold_true)
                    fmt_list.append(bottom_border)

                if bool_blank:
                    fmt_dict = {k: v for d in fmt_list for k, v in d.items()}
                    fmt_master[ir] = wb.add_format(fmt_dict)
                    ws.write_blank(row_current, col_current + ir, None, cell_format=fmt_master[ir])
                else:
                    if isinstance(value, str):
                        fmt_dict = {k: v for d in fmt_list for k, v in d.items()}
                        fmt_master[ir] = wb.add_format(fmt_dict)
                        ws.write_string(row_current, col_current + ir, value, cell_format=fmt_master[ir])
                    else:
                        raise Exception("Numeric type not expected")

                if bool_lastrow:
                    if fld in ['Words']:
                        ws.set_column(col_current + ir, col_current + ir, width=15)
                    elif fld in ['Time']:
                        ws.set_column(col_current + ir, col_current + ir, width=7)

    print("Exported file {}".format(export_filename))


def run_lyrics_analysis(song_duration, directory: str = None, bref: bool = False) -> pd.DataFrame:
    """Runs through analysis process"""
    word_length_filename = "ssb_word_length.csv"
    encoder_read = "cp1252"
    if bref:
        word_length_filename = "bref_word_length.csv"
        encoder_read = "utf-8"

    lyrics_data = read_lyric_data(path=os.path.join(directory, word_length_filename), encode=encoder_read)
    notes_data = create_time_columns(df=lyrics_data, song_duration=song_duration)
    export_data(notes_data, path_directory=directory, song_duration=song_duration, bool_bref=bref)

    return notes_data
