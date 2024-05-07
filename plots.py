import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage import gaussian_filter
import numpy as np


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


def create_grid():
    x = np.arange(-25, 25, 10)
    y = np.arange(-42.5, 42.5, 10)
    return x, y

def get_grid_cell(x, y, x_coord, y_coord):
    x_cell = np.digitize(x_coord, x)
    y_cell = np.digitize(y_coord, y)
    return x_cell, y_cell

def plot_avg_xg_by_grid_cell(grid, x, y):
    fig, ax = plt.subplots()
    c = ax.pcolormesh(y, x, grid, cmap='viridis')
    fig.colorbar(c, ax=ax)
    plt.show()