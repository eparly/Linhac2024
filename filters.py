def neutral_zone_filter(possessions):
    # filter out possessions that start in the neutral zone
    # xadjcoord between -25 and 25
    neutral_zone = []
    for possession in possessions:
        if possession[0]['xadjcoord'] >= -25 and possession[0]['xadjcoord'] <= 25:
            neutral_zone.append(possession)
    return neutral_zone

def filter_events(xg_and_time):
    events = ['pass', 'puckprotection', 'carry', 'controlledentryagainst']
    filtered = {}
    for event in events:
        filtered[event] = xg_and_time[event]
    return filtered