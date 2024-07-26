from app import db
from datetime import datetime

class ElevatorCall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    current_floor = db.Column(db.String(10), nullable=False)
    destination_floor = db.Column(db.String(10), nullable=False)
    is_external_call = db.Column(db.Boolean, nullable=False)
    elevator_at_rest = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<ElevatorCall {self.id}: {self.current_floor} to {self.destination_floor}>'

class ElevatorState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    current_floor = db.Column(db.String(10), nullable=False)
    is_at_rest = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<ElevatorState {self.id}: Floor {self.current_floor}, {"At Rest" if self.is_at_rest else "Busy"}>'