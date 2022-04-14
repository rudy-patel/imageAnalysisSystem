import enum

# This enum holds the camera mode states
class CameraMode(enum.Enum):
    FACIAL_RECOGNITION = "FACIAL_RECOGNITION"
    SHAPE_DETECTION = "SHAPE_DETECTION"

# This enum holds the camera status states
class CameraStatus(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"