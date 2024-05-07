import numpy as np
import math

from plots import get_grid_cell


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