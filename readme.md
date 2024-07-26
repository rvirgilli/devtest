# Elevator Rest Predictor

## Overview
This project is designed to collect and store meaningful data about elevator usage, specifically to feed a Machine Learning (ML) system that will try to predict the optimal resting floor for an elevator when it's not in use. 

## Our Solution

### Data Collection and Storage
We record the following data for each elevator call:
- Timestamp of the call
- Current floor
- Destination floor
- Whether the call is from inside or outside the elevator
- Whether the elevator was at rest when called

This data structure was chosen because it captures the essential information needed to analyze patterns in elevator usage and predict optimal resting positions.

### System Integration
The elevator control system will interact with our API to:
1. Send information about new elevator calls
2. Update the elevator's resting state

The ML system can then retrieve the relevant data through our API for analysis and prediction. The key insight here is that the most valuable data for determining the optimal resting floor are the calls made when the elevator is already at rest. These calls represent instances where the elevator's current resting position either was or wasn't ideal.

By analyzing patterns in these specific calls, the ML system can learn which floors are most frequently requested when the elevator is idle, potentially at different times of day or days of the week. This information is crucial for predicting where the elevator should rest to minimize response times for future calls.

To facilitate this, our API provides a way to filter and retrieve only the calls made when the elevator was at rest. This can be done by setting the `at_rest_only` parameter to "true" when calling the `/get_calls` endpoint. For example:

### Business Rules
Here are the business rules considered for this project:
- Validation of floor numbers against the building configuration
- Checking if calls are made within operational hours

The parameters for these rules are configurable via a JSON file.

## How to Run the System
1. Initialize the database: `python init_db.py`
2. Start the server: `python main.py`

The API will be available at `http://localhost:5000`.

## API Endpoints

### Record Elevator Call
- **URL**: `/elevator_call`
- **Method**: POST
- **Body**:
  ```json
  {
    "current_floor": "string",
    "destination_floor": "string",
    "is_external_call": boolean
  }
- **Response**: 201 Call logged and elevator set to busy

### Set Elevator to Rest
- **URL**: `/elevator_at_rest`
- **Method**: POST
- **Body**:
  ```json
  {
    "current_floor": "string"
  }
- **Response**: 201 Elevator set to rest

### Retrieve Calls
- **URL**: `/get_calls`
- **Method**: GET
- **Query Parameters**: 
  - `at_rest_only` (optional): Set to "true" to retrieve only calls made when the elevator was at rest
- **Response**: 200 OK with JSON array of call data

## Testing
Run all tests using the command `pytest` in the project root.

Our test suite includes:
1. Tests for data models
2. API endpoint tests
3. Business rule validation tests
4. A test that generates 200 random elevator calls, filters those made at rest, exports them to CSV, and verifies data integrity and count.

## Project Structure
- `main.py`: Application entry point
- `app/`: Core application code
  - `models.py`: Database models
  - `routes.py`: API endpoints
  - `utils.py`: Utility functions
- `config/`: Configuration files
- `tests/`: Test suite
- `init_db.py`: Database initialization script

## Possible Improvements
- Implement elevator controller logic
- Enhance data collection:
  - Track elevator movement direction (up/down)
  - Monitor elevator capacity
  - Record door open/close times
  - Log maintenance events
- Add support for multiple elevators

## Personal Experience

Working on this project provided valuable experience in modeling a real-world scenario. Identifying the most relevant data for predicting optimal rest floors was particularly challenging and rewarding.

I utilized a Language Learning Model (LLM) extensively during the debugging phase. This tool was crucial in structuring the solution and implementing effective tests.

Initially, I misunderstood the scope and began building a full elevator logic system. After realizing the need to focus on data collection, I adjusted my approach. This project took longer than the suggested 4 hours, but it was a valuable learning experience.

While I have experience with APIs, this project reinforced my understanding of API design and motivated me to further develop my skills in Flask and API development.

Overall, this project was a beneficial experience. I hope my solution aligns with your expectations and demonstrates my ability to adapt and learn. Regardless of the outcome, I have gained valuable insights from tackling this real-world problem through coding.