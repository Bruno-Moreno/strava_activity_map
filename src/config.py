MAP_CENTER = {"lat": -33.55, "lon": -70.60}

ACTIVITY_TYPE_BLACKLIST = ["WeightTraining", "Workout", "VirtualRide", "Treadmill"]

ACTIVITY_COLOR_MAP = {
    "Run": "#ff6b6b",
    "Ride": "#4ecdc4",
    "Walk": "#45b7d1",
    "Hike": "#96ceb4",
    "Swim": "#feca57",
    "WeightTraining": "#a29bfe",
    "Snowboard": "#74b9ff",
    "Tennis": "#fdcb6e",
}

TRAINING_LOG_WHITELIST = [
    "Run",
    "WeightTraining",
    "Swim",
    "Ride",
    "Snowboard",
    "Tennis",
]
TRAINING_LOG_PATH = "training_log.csv"
TRAINING_LOG_DEFAULT_DAYS = 7
TRAINING_LOG_GAP_HOURS = 48
