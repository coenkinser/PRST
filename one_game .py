import pandas as pd
from glob import glob
import numpy as np
from sportypy.surfaces.football import NFLField
from scipy.spatial.distance import cdist

# Read CSV files into Pandas DataFrames
games = pd.read_csv('games.csv')
plays = pd.read_csv('plays.csv')
players = pd.read_csv('players.csv')

OFFENSE_POSITIONS = ['QB', 'TE', 'T', 'WR', 'G', 'RB', 'C', 'FB', 'LS']
DEFENSE_POSITIONS = ['DE', 'NT', 'SS', 'FS', 'OLB', 'DT', 'CB', 'ILB', 'MLB', 'LS', 'DB']

tracking_files = glob("tracking*.csv")

# Read all CSV files into a single DataFrame using a list comprehension
tracking = pd.concat([pd.read_csv(file) for file in tracking_files], ignore_index=True)

# Filter tracking data for a specific game
#tracking = tracking[tracking['gameId'] == 2022091103].copy()

# Make all plays go from left to right
tracking['x'] = np.where(tracking['playDirection'] == 'left', 120 - tracking['x'], tracking['x'])
tracking['y'] = np.where(tracking['playDirection'] == 'left', 160 / 3 - tracking['y'], tracking['y'])

# Flip player direction and orientation
flip_condition = tracking['playDirection'] == 'left'
tracking['dir'] = np.where(flip_condition, tracking['dir'] + 180, tracking['dir'])
tracking['dir'] = np.where(tracking['dir'] > 360, tracking['dir'] - 360, tracking['dir'])
tracking['o'] = np.where(flip_condition, tracking['o'] + 180, tracking['o'])
tracking['o'] = np.where(tracking['o'] > 360, tracking['o'] - 360, tracking['o'])

# Merge only the necessary columns from the 'players' DataFrame
tracking = pd.merge(players[['nflId', 'position']], tracking, on='nflId', how='left')
tracking = pd.merge(plays[['playId','gameId','ballCarrierId']], tracking, on=['gameId', 'playId'], how='left')

# Vectorize the custom function for better performance
vectorized_custom_function = np.vectorize(lambda position: 'O' if position in OFFENSE_POSITIONS else ('D' if position in DEFENSE_POSITIONS else 'F'))
tracking['Side'] = vectorized_custom_function(tracking['position'])

snaps = tracking.groupby('nflId').agg(
    snaps=('playId', lambda x: x.nunique())
).reset_index()

tracking = pd.merge(tracking, snaps, on=['nflId'])


tracking.to_csv('one_game.csv')
