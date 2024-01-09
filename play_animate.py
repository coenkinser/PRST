import pandas as pd
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
from sportypy.surfaces.football import NFLField
from matplotlib.animation import FuncAnimation
from scipy.spatial.distance import cdist

tracking = pd.read_csv('one_play_tracking.csv')

fig, ax = plt.subplots(1, 1)
NFLField().draw(ax = ax)


        

example_play = tracking.query('gameId == 2022091103 and playId == 1126').copy()

for index, row in example_play.iterrows():
    if row['nflId'] == row['ballCarrierId']:
        example_play.at[index, 'club'] = 'football'


#example_play.to_csv('example_play2.csv')


example_play['pt_color'] = np.select(
    [
        example_play['club'] == 'CIN',
        example_play['club'] == 'PIT',
        example_play['club'] == 'football'
    ],
    ['red', 'blue', 'yellow']
)

# Initialize empty scatter plot (will be updated in the animation)
scatter = ax.scatter([], [], c=[], s=50, marker='o')

def update(frame):
    # Update scatter plot data based on frame
    indices = example_play["frameId"] == frame
    scatter.set_offsets(np.column_stack(((example_play["x"][indices]) - 120/2, (example_play["y"][indices]) - 53.3/2)))
    
    scatter.set_sizes(example_play["value"][indices]*40+40)
    scatter.set_color([plt.cm.colors.to_rgba(color) for color in example_play["pt_color"][indices]])
    return scatter,


# Create the animation
animation = FuncAnimation(fig, update, frames=np.unique(example_play["frameId"]), interval=100, blit=True)

plt.show()
