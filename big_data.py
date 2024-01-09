import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

tracking_new = pd.read_csv('one_game.csv')
#tracking_new = tracking_new.query('gameId == 2022091103 and playId == 1126 and frameId == 5').copy()

def calculate_relative_vel(group):
    relative_vel_list = []
    nflId_list = []
    playId_list = []
    frameId_list = []
    ball_carrier = group[group['nflId'] == group['ballCarrierId']].iloc[0]

    for _, row in group.iterrows():
        vector_to_ball_carrier = ball_carrier[['x', 'y']].values - row[['x', 'y']].values

        direction_angle_rad = np.radians(row['dir'])
        player_orientation_vector = np.array([np.cos(np.radians(row['o'])), np.sin(np.radians(row['o']))])
        player_vel_vector = row['s'] * np.array([np.cos(np.radians(row['dir'])), np.sin(np.radians(row['dir']))])
        ball_vel_vector = ball_carrier['s'] * np.array([np.cos(np.radians(ball_carrier['dir'])), np.sin(np.radians(ball_carrier['dir']))])

        vel_vector = player_vel_vector-ball_vel_vector

        distance = np.linalg.norm(vector_to_ball_carrier)

        if distance==0:
            mag_vel=0
            sign=1
        else:
            unit_vector=vector_to_ball_carrier/distance

            mag_vel = np.linalg.norm(vel_vector)

            sign = np.dot(unit_vector, vel_vector)

        value=mag_vel
        if sign<0:
            value=mag_vel*-1

        if distance==0:
            value=0

        if np.dot(vector_to_ball_carrier, player_orientation_vector)<=0 and np.dot(vector_to_ball_carrier, player_vel_vector)<=0:
            value=0

        if row['Side']!='D':
            value=0
            
        value=value/10
        '''
        else:
            value=value/(1+distance)
            value=np.exp(value / 20)
        '''
        relative_vel_list.append(value)
        nflId_list.append(row['nflId'])
        playId_list.append(row['playId'])
        frameId_list.append(row['frameId'])

    return pd.DataFrame({'value': relative_vel_list, 'nflId': nflId_list, 'playId': playId_list, 'frameId': frameId_list})



# Calculate radial acceleration and create DataFrame
dataf = tracking_new.groupby(['gameId', 'playId', 'frameId']).apply(calculate_relative_vel).reset_index(drop=True)


def maximum(group):
    best_list = []
    nflId_list = []
    playId_list = []
    frameId_list = []

    high=group['value'].max()
    for _, row in group.iterrows():
        if row['value']>=high:
            best_list.append(1)
        else:
            best_list.append(0)

        nflId_list.append(row['nflId'])
        playId_list.append(row['playId'])
        frameId_list.append(row['frameId'])

    return pd.DataFrame({'best': best_list, 'nflId': nflId_list, 'playId': playId_list, 'frameId': frameId_list})

best_df = dataf.groupby('playId').apply(maximum).reset_index(drop=True)

# Merge on index
tracking_new = pd.merge(tracking_new, dataf, on=['nflId', 'playId', 'frameId'])
tracking_new = pd.merge(tracking_new, best_df, on=['nflId', 'playId', 'frameId'])

tracking_new = tracking_new[tracking_new['snaps'] > 0]
tracking_new = tracking_new[tracking_new['value'] != 1]
# Extract unique defensive player names
unique_players = tracking_new[tracking_new['Side'] == 'D']['displayName'].unique()

# Calculate mean frame value for each defensive player and output values to CSV
final_results = tracking_new[tracking_new['Side'] == 'D'].groupby(['displayName', 'position'], as_index=False).agg({'value': ['mean', 'sum']})
final_results.columns = ['Player', 'Position', 'Mean_Value', 'Total_Value']

# Calculate the sum of the 'best' column for each defensive player
best_sum = tracking_new[tracking_new['Side'] == 'D'].groupby(['displayName', 'position'], as_index=False)['best'].sum()

# Merge the 'best_sum' DataFrame with the 'final_results' DataFrame on the 'Player' and 'Position' columns
final_results = pd.merge(final_results, best_sum, left_on=['Player', 'Position'], right_on=['displayName', 'position'], how='left')

# Drop redundant columns from the merged DataFrame
final_results.drop(['displayName', 'position'], axis=1, inplace=True)

# Rename the new column to 'Best_Sum'
final_results.rename(columns={'best': 'Best_Sum'}, inplace=True)

# Output the results to CSV
final_results.to_csv('Data.csv', index=False)
