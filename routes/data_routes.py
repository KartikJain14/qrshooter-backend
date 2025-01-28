from flask import Blueprint, jsonify, abort
from controllers.data_controller import (
    get_events_for_day, 
    get_items
    )

data_routes = Blueprint('event_routes', __name__)

@data_routes.route('/events/<int:day>', methods=['GET'])
def get_events(day):
    events = get_events_for_day(day)
    if events is None:
        abort(404, description=f"Events for day {day} not found")
    return jsonify(events)

@data_routes.route('/items', methods=['GET'])
def get_items_route():
    items = get_items()
    if items is None:
        abort(404, description="Items not found")
    return jsonify(items)