import os

import pandas as pd

import anthem_utils as aut

directory = os.getcwd()

# data retrieved from https://www.covers.com/nfl/super-bowl/props/national-anthem
score_data = pd.read_csv(os.path.join(directory, 'score_anthem_data.csv'))

# 'Time' is a string data type, need to convert to 'Seconds' (integer data type)
score_data['Seconds'] = score_data.apply(lambda x: aut.minutes_to_seconds(x['Time']), axis=1)
target_time = 63

# run analysis on Star Spangled Banner lyrics
notes_data = aut.run_lyrics_analysis(song_duration=target_time, directory=directory, bref=True)
