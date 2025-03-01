from flask import Blueprint, jsonify, abort
from controllers.data_controller import (
    get_schedule, 
    get_items,
    get_events
    )

data_routes = Blueprint('event_routes', __name__)

@data_routes.route('/schedule', methods=['GET'])
def schedule():
    return jsonify(get_schedule())

@data_routes.route('/items', methods=['GET'])
def get_items_route():
    return jsonify(get_items())

@data_routes.route('/events', methods=['GET'])
def events():
    return jsonify(get_events())