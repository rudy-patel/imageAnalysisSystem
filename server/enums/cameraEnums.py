import enum

class CameraMode(enum.Enum):
    FACIAL_RECOGNITION = "FACIAL_RECOGNITION"
    FAULT_DETECTION = "FAULT_DETECTION"

class CameraStatus(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"