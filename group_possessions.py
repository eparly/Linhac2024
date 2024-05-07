import pandas as pd
import time as t
from filters import neutral_zone_filter
from get_xg_time import get_xg_by_event
from plots import plot_event_xg

data = pd.read_csv('Linhac24_Sportlogiq.csv')
data = data[data['currentpossession'].notna()]

#get rows where possession changes occur, returns boolean array

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

    return possessions


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


# lengths_by_event = get_possession_lengths_by_event(grouped_neutral_2)
# plot_possession_lengths(lengths_by_event)


# time_by_event = get_possession_lengths_by_event(grouped_neutral_2)
# plot_event_time(time_by_event['pass'], binsize=2)

xg_by_event = get_xg_by_event(grouped_neutral_2)

plot_event_xg(xg_by_event['carry'], binsize=6)









