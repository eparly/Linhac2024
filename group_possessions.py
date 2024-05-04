import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import math
import time as t
import pickle
import seaborn as sns
from scipy.ndimage import gaussian_filter



data = pd.read_csv('Linhac24_Sportlogiq.csv')
data = data[data['currentpossession'].notna()]

#get rows where possession changes occur, returns boolean array

#147249
def possession_changes(data):
    data['prev_possession'] = data['currentpossession'].shift()

    #need to make sure that the 'gameid' column is the same for all rows in a given possession
    #if not, the possession has changed
    data['possession_change'] = ((data['prev_possession'] == data['currentpossession'] - 1) | 
                             (data['gameid'] != data['gameid'].shift()))
    
    if data['possession_change'].isna().any():
        data['possession_change'] = data['currentpossession']
    return data['possession_change'] == 1


def group_possessions(data):
    possession_change = possession_changes(data)
    #split the data into possessions
    #store each possession as a dataframe in a list

    possessions = []
    current_possession = []
    for index, row in data.iterrows():
        if possession_change[index]:
            if (len(current_possession) == 0):
                a=0
                continue
            possessions.append(current_possession)

            current_possession = []
        current_possession.append(row)

    # with open('grouped_possessions.pkl', 'wb') as f:
    #     pickle.dump(possessions, f)

    return possessions


def neutral_zone_filter(possessions):
    # filter out possessions that start in the neutral zone
    # xadjcoord between -25 and 25
    neutral_zone = []
    for possession in possessions:
        if possession[0]['xadjcoord'] >= -25 and possession[0]['xadjcoord'] <= 25:
            neutral_zone.append(possession)
    return neutral_zone


def get_possession_starts(possessions):
    starts = []
    for possession in possessions:
        starts.append(possession[0])
    return starts

def group_by_event(neutral):
    grouped = {}
    for sub_array in neutral:
        event = sub_array[0]['eventname']  # assuming 'event' is a key in the first dictionary of each sub-array
        if(event == 'pass'):
            a=0
        if event in grouped:
            grouped[event].append(sub_array)
        else:
            grouped[event] = [sub_array]
    return grouped

def group_by_second_event(neutral):
    grouped = {}
    for sub_array in neutral:
        # possibly limit to something higher, like 4 or 5
        if len(sub_array) < 2:
            continue
        event = sub_array[1]['eventname']  # assuming 'event' is a key in the first dictionary of each sub-array
        if event in grouped:
            grouped[event].append(sub_array)
        else:
            grouped[event] = [sub_array]
    return grouped

def get_avg_xg(possessions):
    xg = []
    for possession in possessions:
        xgs = [x['xg_allattempts'] for x in possession if math.isnan(x['xg_allattempts']) == False]
        xg.append(sum(xgs))
    return np.mean(xg)

def get_avg_xg_by_event(grouped):
    xg = {}
    for event in grouped:
        xg[event] = get_avg_xg(grouped[event])
    return xg


def get_avg_time(possessions):
    time = []
    for possession in possessions:
        times = [x['compiledgametime'] for x in possession]
        time.append(times[-1] - times[0])
        if time[-1] < 0:
            a=0
    return np.mean(time)

def get_avg_time_by_event(grouped):
    time = {}
    for event in grouped:
        time[event] = get_avg_time(grouped[event])
    return time

def collect_xg_and_time_by_event(xg, time):
    keys = xg.keys()
    xg_and_time = {}
    for key in keys:
        xg_and_time[key] = [xg[key], time[key]]
    return xg_and_time



start_time = t.time()
poss = group_possessions(data)
# with open('grouped_possessions.pkl', 'rb') as f:
#     poss = pickle.load(f)
print("--- group_possessions: %s seconds ---" % (t.time() - start_time))

start_time = t.time()
neutral = neutral_zone_filter(poss)
print("--- neutral_zone_filter: %s seconds ---" % (t.time() - start_time))


start_time = t.time()
grouped_neutral_2 = group_by_second_event(neutral)
print("--- group_by_second_event: %s seconds ---" % (t.time() - start_time))


# avg_xg = get_avg_xg(neutral)
# avg_time = get_avg_time(neutral)
# xg_by_event = get_avg_xg_by_event(grouped_neutral_2)
# time_by_event = get_avg_time_by_event(grouped_neutral_2)
a=0
# xg_and_time = collect_xg_and_time_by_event(xg_by_event, time_by_event)

# filter xg_and_time to only include the following:
# pass, puckprotection, lpr, dumpin, shot, carry, controlledentryagainst

def filter_events(xg_and_time):
    events = ['pass', 'puckprotection', 'carry', 'controlledentryagainst']
    filtered = {}
    for event in events:
        filtered[event] = xg_and_time[event]
    return filtered

# xg_time_filtered = filter_events(xg_and_time)


# picture a chart: x axis is the length of each possession, y axis is the xg of each possession
# Each point is a possession, color coded by the event that starts the possession (or second event)

def get_xg_and_time_of_all_possessions(possessions):
    time_xg = []
    for possession in possessions:
        xg = sum([x['xg_allattempts'] for x in possession if math.isnan(x['xg_allattempts']) == False])
        time = possession[-1]['compiledgametime'] - possession[0]['compiledgametime']
        time_xg.append([time, xg])
    return time_xg

def get_xg_and_time_by_event(grouped):
    xg_and_time = {}
    for event in grouped:
        xg_and_time[event] = get_xg_and_time_of_all_possessions(grouped[event])
    return xg_and_time

# def plot_xg_and_time(xg_and_time):
#     fig, ax = plt.subplots()

#     # Calculate event type frequencies
#     event_types = [key for key in xg_and_time]
#     event_type_counts = np.array([len(xg_and_time[key]) for key in xg_and_time])
#     normalized_counts = (event_type_counts - event_type_counts.min()) / (event_type_counts.max() - event_type_counts.min())
#     event_type_count_dict = dict(zip(event_types, normalized_counts))

#     def get_alpha(event_type):
#         return 0.2+0.8*event_type_count_dict[event_type]
    
#     for key in xg_and_time:
#         time_xg = xg_and_time[key]
#         time = [x[0] for x in time_xg]
#         xg = [x[1] for x in time_xg]
#         ax.scatter(time, xg, s=50, label=key, alpha=get_alpha(key))
#     ax.legend()
#     plt.xlabel('Time')
#     plt.ylabel('xG')
#     plt.title('Scatter Plot of Time vs. xG with Event Types')
#     plt.show()

#     ax.legend()
#     plt.show()

def plot_xg_and_time(xg_and_time):
    fig, axs = plt.subplots(2, 2, figsize=(10, 8), sharex=True, sharey=True)
    fig.suptitle('Scatter Plot of Time vs. xG with Event Types')

    event_types = list(xg_and_time.keys())
    event_type_colors = ['b', 'g', 'r', 'c']  # You can define your own colors
    
    for i, ax in enumerate(axs.flat):
        event_type = event_types[i]
        time_xg = xg_and_time[event_type]
        time = [x[0] for x in time_xg]
        xg = [x[1] for x in time_xg]
        ax.scatter(time, xg, s=50, c=event_type_colors[i], label=event_type)
        ax.set_title(event_type)
        ax.legend()
        
    plt.xlabel('Time')
    plt.ylabel('xG')
    plt.tight_layout()
    plt.show()

# filtered_neutral = filter_events(grouped_neutral_2)
# time_xg = get_xg_and_time_by_event(filtered_neutral)
# plot_xg_and_time(time_xg)

a=0


# or, do this for the avg possession length and xg for each event

# picture another chart: a probability distribution of the length of possessions for each event

def get_possession_lengths(possessions):
    lengths = []
    for possession in possessions:
        length = possession[-1]['compiledgametime'] - possession[0]['compiledgametime']
        lengths.append((length, possession[0]['xadjcoord'], possession[0]['yadjcoord']))
    return lengths

def get_possession_lengths_by_event(grouped):
    lengths = {}
    events = ['pass', 'puckprotection', 'dumpin', 'carry', 'controlledentryagainst']

    for event in events:
        lengths[event] = get_possession_lengths(grouped[event])
    return lengths

def plot_possession_lengths(lengths):
    num_keys = len(lengths)
    fig, axs = plt.subplots(num_keys, 1, figsize=(5, num_keys*2))  # adjust the size as needed

    # Determine the global min and max across all lengths
    global_min = min(min(lengths[key]) for key in lengths)
    global_max = max(max(lengths[key]) for key in lengths)

    for i, key in enumerate(lengths):
        sns.kdeplot(lengths[key], ax=axs[i], fill=True, clip = (0, 12.5))
        axs[i].set_title(key)
        axs[i].set_xlim(global_min, 20)  # set the same x-axis limits for all subplots

    plt.tight_layout()
    plt.show()

# lengths_by_event = get_possession_lengths_by_event(grouped_neutral_2)
# plot_possession_lengths(lengths_by_event)
# a=0


# or do this for the distribution of xg for each event

def plot_xg_distributions(xg_by_event):
    num_keys = len(xg_by_event)
    fig, axs = plt.subplots(num_keys, 1, figsize=(5, num_keys*2))  # adjust the size as needed

    # Determine the global min and max across all lengths
    # global_min = min(min(xg_by_event[key]) for key in xg_by_event)
    # global_max = max(max(xg_by_event[key]) for key in xg_by_event)
    

    for i, key in enumerate(xg_by_event):
        sns.kdeplot(xg_by_event[key], ax=axs[i], fill=True, clip=(0.01, 0.075))
        axs[i].set_title(key)
        axs[i].set_xlim(0, 0.1)  # set the same x-axis limits for all subplots

    plt.tight_layout()
    plt.show()

#repeat the get_possession_lengths_by_event for xg
    
def get_xg_by_event(grouped):
    xg_by_event = {}
    events = ['pass', 'puckprotection', 'carry', 'controlledentryagainst']

    for event in events:
        event_xg = []
        for possession in grouped[event]:
            xgs = [x['xg_allattempts'] for x in possession if math.isnan(x['xg_allattempts']) == False]
            event_xg.append((sum(xgs), possession[0]['xadjcoord'], possession[0]['yadjcoord']))
        xg_by_event[event] = event_xg
    return xg_by_event

def bin_data(data, bins):
    x = [n[1] for n in data]
    y = [n[2] for n in data]
    xg = [n[0] for n in data]

    x_bins = np.arange(min(x), max(x) + bins, bins)
    y_bins = np.arange(min(y), max(y) + bins, bins)

    _, x_edge, y_edge = np.histogram2d(x, y, bins=[x_bins, y_bins])

    bin_indices_x = np.digitize(x, x_bins) -1
    bin_indices_y = np.digitize(y, y_bins) -1

    avg_xg = np.zeros((len(x_bins)-1, len(y_bins)-1))
    bin_samples_count = np.zeros_like(avg_xg)


    for i in range(len(x)):
        avg_xg[bin_indices_x[i], bin_indices_y[i]] += xg[i]
        bin_samples_count[bin_indices_x[i], bin_indices_y[i]] += 1

    avg_xg /= bin_samples_count
    avg_xg[np.isnan(avg_xg)] = 0
    return avg_xg, x_edge, y_edge

def plot_event_xg(data_array, binsize=2):
    avg_xg, x_bins, y_bins = bin_data(data_array, binsize)
    avg_xg_gaussian = gaussian_filter(avg_xg, sigma=1)

    # Create a plot
    plt.figure(figsize=(8, 6))
    plt.imshow(avg_xg_gaussian, extent=[x_bins[0], x_bins[-1], y_bins[0], y_bins[-1]], origin='lower', cmap='viridis')
    plt.colorbar(label='Average xg')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Average XG - Passing the Puck')
    plt.grid(visible=True)
    plt.show()

def plot_event_time(data_array, binsize=2):
    avg_time, x_bins, y_bins = bin_data(data_array, binsize)
    avg_time_gaussian = gaussian_filter(avg_time, sigma=1)

    # Create a plot
    plt.figure(figsize=(8, 6))
    plt.imshow(avg_time_gaussian, extent=[x_bins[0], x_bins[-1], y_bins[0], y_bins[-1]], origin='lower', cmap='viridis')
    plt.colorbar(label='Average Time')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Average Time - Passing the Puck')
    plt.grid(visible=True)
    plt.show()

# time_by_event = get_possession_lengths_by_event(grouped_neutral_2)
# plot_event_time(time_by_event['pass'], binsize=2)

xg_by_event = get_xg_by_event(grouped_neutral_2)

plot_event_xg(xg_by_event['carry'], binsize=6)

bin_size = 4
# xg_by_event_filtered = filter_events(xg_by_event)
# plot_xg_distributions(xg_by_event)
a=0

# or do this for the distribution of xg for each event
# lay these charts on top of eachother to see a difference?

# picture a chart: On an overlay of the neutral zone, plot the event from that location to maximize xg
# bucket the possessions by the starting location of the possession, find which event results in largest avg xg
# repeat for each bucket of locations on the ice

# need to create a grid to bin the x and y coordinates into, then find the average xg per event per grid cell

def create_grid():
    x = np.arange(-25, 25, 10)
    y = np.arange(-42.5, 42.5, 10)
    return x, y

def get_grid_cell(x, y, x_coord, y_coord):
    x_cell = np.digitize(x_coord, x)
    y_cell = np.digitize(y_coord, y)
    return x_cell, y_cell

def get_avg_xg_by_grid_cell(possessions, x, y):
    grid = np.zeros((len(x), len(y)))
    counts = np.zeros((len(x), len(y)))
    for possession in possessions:
        x_coord = possession[0]['xadjcoord']
        y_coord = possession[0]['yadjcoord']
        x_cell, y_cell = get_grid_cell(x, y, x_coord, y_coord)
        xg = sum([x['xg_allattempts'] for x in possession if math.isnan(x['xg_allattempts']) == False])
        grid[x_cell-1, y_cell-1] += xg
        counts[x_cell-1, y_cell-1] += 1
    grid = np.divide(grid, counts, out=np.zeros_like(grid), where=counts!=0)
    return grid

def plot_avg_xg_by_grid_cell(grid, x, y):
    fig, ax = plt.subplots()
    c = ax.pcolormesh(y, x, grid, cmap='viridis')
    fig.colorbar(c, ax=ax)
    plt.show()

# x, y = create_grid()
# grid = get_avg_xg_by_grid_cell(neutral, x, y)
# plot_avg_xg_by_grid_cell(grid, x, y)
# a=0






# Cross validation: split the data into 4 or 5 parts, see if the data from each section agrees with the conclusions drawn from the whole dataset
