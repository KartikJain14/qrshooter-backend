import json

def get_schedule():
    try:
        with open(f'data/schedule.json', 'r', encoding='utf-8') as f:
            events = json.load(f)
        return events
    except FileNotFoundError:
        return {'error': 'File not found'}

def get_items():
    try:
        with open('data/items.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
        return items
    except FileNotFoundError:
        return {'error': 'File not found'}
    
def get_events():
    try:
        with open('data/events.json', 'r', encoding='utf-8') as f:
            events = json.load(f)
        return events
    except FileNotFoundError:
        return {'error': 'File not found'}