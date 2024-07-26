import pytest
from app import create_app, db
from app.models import ElevatorCall, ElevatorState
from datetime import datetime


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


def test_new_elevator_call(app):
    with app.app_context():
        call = ElevatorCall(current_floor='G', destination_floor='5', is_external_call=True, elevator_at_rest=True)
        db.session.add(call)
        db.session.commit()

        assert call.id is not None
        assert call.current_floor == 'G'
        assert call.destination_floor == '5'
        assert call.is_external_call is True
        assert call.elevator_at_rest is True
        assert isinstance(call.timestamp, datetime)


def test_new_elevator_state(app):
    with app.app_context():
        state = ElevatorState(current_floor='3', is_at_rest=False)
        db.session.add(state)
        db.session.commit()

        assert state.id is not None
        assert state.current_floor == '3'
        assert state.is_at_rest is False
        assert isinstance(state.timestamp, datetime)


def test_elevator_call_representation(app):
    with app.app_context():
        call = ElevatorCall(current_floor='G', destination_floor='5', is_external_call=True, elevator_at_rest=True)
        assert repr(call) == '<ElevatorCall None: G to 5>'


def test_elevator_state_representation(app):
    with app.app_context():
        state = ElevatorState(current_floor='3', is_at_rest=False)
        assert repr(state) == '<ElevatorState None: Floor 3, Busy>'