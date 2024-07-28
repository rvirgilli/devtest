from flask import request, jsonify
from app import db
from app.models import ElevatorCall, ElevatorState
from app.utils import is_valid_floor, is_within_operational_hours
from datetime import datetime


def init_app(app):
    @app.route('/elevator_call', methods=['POST'])
    def log_elevator_call():
        data = request.json

        if not is_valid_floor(data['current_floor']) or not is_valid_floor(data['destination_floor']):
            return jsonify({"error": "Invalid floor"}), 400

        last_state = ElevatorState.query.order_by(ElevatorState.timestamp.desc()).first()

        new_call = ElevatorCall(
            current_floor=data['current_floor'],
            destination_floor=data['destination_floor'],
            is_external_call=data['is_external_call'],
            elevator_at_rest=last_state.is_at_rest if last_state else True
        )
        db.session.add(new_call)

        # Set elevator to busy
        new_state = ElevatorState(
            current_floor=data['current_floor'],
            is_at_rest=False
        )
        db.session.add(new_state)

        db.session.commit()
        return jsonify({"message": "Call logged and elevator set to busy"}), 201

    @app.route('/elevator_at_rest', methods=['POST'])
    def set_elevator_at_rest():
        data = request.json
        new_state = ElevatorState(
            current_floor=data['current_floor'],
            is_at_rest=True
        )
        db.session.add(new_state)
        db.session.commit()
        return jsonify({"message": "Elevator set to rest"}), 201

    @app.route('/get_calls', methods=['GET'])
    def get_calls():
        at_rest_only = request.args.get('at_rest_only', 'false').lower() == 'true'
        is_external_call = request.args.get('is_external_call', None)

        query = ElevatorCall.query
        if at_rest_only:
            query = query.filter_by(elevator_at_rest=True)
        if is_external_call is not None:
            is_external_call = is_external_call.lower() == 'true'
            query = query.filter_by(is_external_call=is_external_call)

        calls = query.order_by(ElevatorCall.timestamp).all()

        return jsonify([{
            'timestamp': call.timestamp.isoformat(),
            'current_floor': call.current_floor,
            'destination_floor': call.destination_floor,
            'is_external_call': call.is_external_call,
            'elevator_at_rest': call.elevator_at_rest
        } for call in calls]), 200

    @app.route('/move_elevator', methods=['POST'])
    def move_elevator():
        data = request.json

        if not is_valid_floor(data['destination_floor']):
            return jsonify({"error": "Invalid floor"}), 400

        last_state = ElevatorState.query.order_by(ElevatorState.timestamp.desc()).first()

        if not last_state or not last_state.is_at_rest:
            return jsonify({"error": "Elevator is busy"}), 400

        new_state = ElevatorState(
            current_floor=data['destination_floor'],
            is_at_rest=True
        )
        db.session.add(new_state)
        db.session.commit()

        return jsonify({"message": "Elevator moved to destination and set to rest"}), 201
