"""
Configuration settings for the V2V Negotiation System
"""

# Simulation Environment
GRID_SIZE = 1000  # pixels
INTERSECTION_SIZE = 100  # pixels (intersection dimensions)
INTERSECTION_CENTER = (GRID_SIZE // 2, GRID_SIZE // 2)

# Communication Settings
V2V_RANGE = 300  # meters (communication range)
V2I_RANGE = 500  # meters (RSU communication range)
COMMUNICATION_DELAY_MS = 50  # milliseconds (average latency)
MESSAGE_LOSS_RATE = 0.02  # 2% message loss rate

# Vehicle Settings
VEHICLE_SPEED_MIN = 10  # pixels per second
VEHICLE_SPEED_MAX = 50  # pixels per second
VEHICLE_DECELERATION = 2  # pixels per second^2
VEHICLE_SIZE = 20  # pixels (for visualization)

# Simulation Parameters
SIMULATION_TIME_STEPS = 1000  # total steps
TIME_STEP_DURATION = 0.1  # seconds per step
FPS = 30  # frames per second for visualization

# AI Predictor Settings
PREDICTION_WINDOW = 10  # steps ahead to predict
COLLISION_THRESHOLD = 30  # pixels (minimum safe distance)
TRAJECTORY_SMOOTHING = 0.8  # exponential smoothing factor

# Road Side Unit (RSU) Settings
RSU_POSITION = INTERSECTION_CENTER
RSU_DECISION_TIME = 0.05  # seconds to make decisions
FCFS_TIMEOUT = 5.0  # seconds before timing out a vehicle

# Logging & Output
DEBUG_MODE = False
SAVE_SIMULATION_DATA = True
DATA_OUTPUT_DIR = "data/"
OUTPUT_GRAPHS_DIR = "outputs/"

# Vehicle Spawn Configuration
SPAWN_POINTS = [
    (50, 500),        # Left side
    (950, 500),       # Right side
    (500, 50),        # Top
    (500, 950),       # Bottom
]

# Test Scenario Configurations
SCENARIOS = {
    'scenario_1': {
        'name': 'Two vehicles perpendicular approach',
        'vehicles': 2,
        'vehicle_speeds': [30, 25],
        'arrival_times': [0, 2],
    },
    'scenario_2': {
        'name': 'Multiple vehicles with varied speeds',
        'vehicles': 4,
        'vehicle_speeds': [20, 35, 28, 40],
        'arrival_times': [0, 1, 2, 3],
    },
    'scenario_3': {
        'name': 'Emergency vehicle priority (simulated)',
        'vehicles': 3,
        'vehicle_speeds': [45, 25, 30],
        'arrival_times': [0, 1, 2],
        'vehicle_types': ['emergency', 'regular', 'regular'],
    },
}
