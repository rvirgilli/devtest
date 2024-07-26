import pytest
import csv
import random
from app import create_app, db
from app.models import ElevatorCall, ElevatorState
from datetime import datetime, timedelta
import json
from unittest.mock import patch


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

def test_log_elevator_call(client, app):
    with app.app_context():
        # Mock datetime to return a time within operational hours (e.g., 14:00)
        mock_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        with patch('app.routes.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = mock_time

            response = client.post('/elevator_call', json={
                'current_floor': 'G',
                'destination_floor': '5',
                'is_external_call': True
            })
            print("Response data:", response.data)
            assert response.status_code == 201
            assert b"Call logged and elevator set to busy" in response.data

            # Check that the call was added to the database
            call = ElevatorCall.query.first()
            assert call is not None
            assert call.current_floor == 'G'
            assert call.destination_floor == '5'
            assert call.is_external_call is True

            # Check that the elevator state was updated
            state = ElevatorState.query.order_by(ElevatorState.timestamp.desc()).first()
            assert state is not None
            assert state.current_floor == 'G'
            assert state.is_at_rest is False


def test_set_elevator_at_rest(client, app):
    with app.app_context():
        response = client.post('/elevator_at_rest', json={
            'current_floor': '5'
        })
        assert response.status_code == 201
        assert b"Elevator set to rest" in response.data

        # Check that the elevator state was updated
        state = ElevatorState.query.order_by(ElevatorState.timestamp.desc()).first()
        assert state is not None
        assert state.current_floor == '5'
        assert state.is_at_rest is True


def test_get_calls(client, app):
    with app.app_context():
        # Add some test data
        call1 = ElevatorCall(current_floor='G', destination_floor='5', is_external_call=True, elevator_at_rest=True)
        call2 = ElevatorCall(current_floor='5', destination_floor='G', is_external_call=False, elevator_at_rest=False)
        db.session.add_all([call1, call2])
        db.session.commit()

        response = client.get('/get_calls')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2

        response = client.get('/get_calls?at_rest_only=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['current_floor'] == 'G'


def test_invalid_floor(client, app):
    with app.app_context():
        response = client.post('/elevator_call', json={
            'current_floor': 'invalid',
            'destination_floor': '5',
            'is_external_call': True
        })
        assert response.status_code == 400
        assert b"Invalid floor" in response.data


def test_outside_operational_hours(client, app):
    with app.app_context():
        # Assuming operational hours are from 06:00 to 22:00
        outside_hours = datetime.now().replace(hour=23, minute=0)

        # Mocking datetime.utcnow() to return a time outside operational hours
        class MockDateTime(datetime):
            @classmethod
            def utcnow(cls):
                return outside_hours

        # Patch datetime in the route function
        import app.routes
        app.routes.datetime = MockDateTime

        response = client.post('/elevator_call', json={
            'current_floor': 'G',
            'destination_floor': '5',
            'is_external_call': True
        })
        assert response.status_code == 400
        assert b"Outside operational hours" in response.data

        # Reset datetime to avoid affecting other tests
        app.routes.datetime = datetime


def test_generate_and_export_calls(client, app):
    with app.app_context():
        # Generate 200 calls
        start_time = datetime(2024, 1, 1, 6, 0)  # Start at 6 AM
        floors = ["B3", "B2", "B1", "G", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        calls_at_rest = 0

        for i in range(200):
            current_floor = random.choice(floors)
            destination_floor = random.choice([f for f in floors if f != current_floor])
            is_external_call = random.choice([True, False])
            is_at_rest = random.choice([True, False])

            if is_at_rest:
                calls_at_rest += 1

            call = ElevatorCall(
                timestamp=start_time + timedelta(minutes=i * 10),  # Calls every 10 minutes
                current_floor=current_floor,
                destination_floor=destination_floor,
                is_external_call=is_external_call,
                elevator_at_rest=is_at_rest
            )
            db.session.add(call)

        db.session.commit()

        print(f"Total calls at rest: {calls_at_rest}")

        # Retrieve calls made when elevator was at rest
        response = client.get('/get_calls?at_rest_only=true')
        assert response.status_code == 200
        data = response.json

        # Export to CSV
        csv_file_path = 'elevator_calls_at_rest.csv'
        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'current_floor', 'destination_floor', 'is_external_call', 'elevator_at_rest']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for call in data:
                writer.writerow({
                    'timestamp': call['timestamp'],
                    'current_floor': call['current_floor'],
                    'destination_floor': call['destination_floor'],
                    'is_external_call': call['is_external_call'],
                    'elevator_at_rest': call['elevator_at_rest']
                })

        # Verify the number of calls exported
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            row_count = sum(1 for row in reader) - 1  # Subtract 1 for header

        print(f"Total calls exported: {row_count}")

        # Assert that the number of exported calls matches the number of calls at rest
        assert row_count == calls_at_rest, f"Expected {calls_at_rest} calls, but exported {row_count}"

        # Verify all exported calls have elevator_at_rest=True
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            assert all(row['elevator_at_rest'] == 'True' for row in
                       reader), "All exported calls should have elevator_at_rest=True"

    # The CSV file will be created in your project directory
    print(f"CSV file created at: {csv_file_path}")