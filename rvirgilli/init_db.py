from app import create_app, db
from app.models import ElevatorState
from app.utils import load_config


def init_db():
    app = create_app()
    config = load_config()

    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if there's already an initial state
        if ElevatorState.query.first() is None:
            # Get initial state from config
            building_config = config.get('building_config', {})
            initial_floor = building_config.get('default_resting_floor')

            if initial_floor is None or initial_floor not in building_config.get('floors', []):
                raise ValueError("Invalid or missing default_resting_floor in configuration")

            # Initialize elevator state
            initial_state = ElevatorState(current_floor=initial_floor, is_at_rest=True)
            db.session.add(initial_state)
            db.session.commit()
            print(f"Initialized elevator state: {initial_floor} floor, at rest.")
        else:
            print("Database already initialized.")


if __name__ == '__main__':
    try:
        init_db()
        print("Database initialization complete.")
    except ValueError as e:
        print(f"Error initializing database: {e}")
        print("Please check your elevator_config.json file.")