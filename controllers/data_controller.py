import json

def get_events_for_day(day):
    try:
        with open(f'data/schedule/day_{day}.json', 'r') as f:
            events = json.load(f)
        return events
    except FileNotFoundError:
        return None

def get_items():
    try:
        with open('data/reedem/items.json', 'r') as f:
            items = json.load(f)
        return items
    except FileNotFoundError:
        return None