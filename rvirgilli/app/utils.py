import json
from pathlib import Path
from datetime import datetime


def load_config():
    config_path = Path(__file__).parent.parent / 'config' / 'elevator_config.json'
    with open(config_path, 'r') as config_file:
        return json.load(config_file)


config = load_config()


def is_valid_floor(floor):
    return floor in config['building_config']['floors']


def is_within_operational_hours(timestamp):
    start_time = datetime.strptime(config['building_config']['operational_hours']['start_time'], '%H:%M').time()
    end_time = datetime.strptime(config['building_config']['operational_hours']['end_time'], '%H:%M').time()

    # Convert timestamp to time object for comparison
    current_time = timestamp.time()

    return start_time <= current_time <= end_time
