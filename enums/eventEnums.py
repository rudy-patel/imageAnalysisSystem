import enum

class EventType(enum.Enum):
    FACIAL_MATCH_SUCCESS = "Face recognized"
    FACIAL_MATCH_FAILED = "New face detected"
    FACIAL_MATCH_ERROR = "Something went wrong"
    FAULT_DETECT_SUCCESS = "Fault detected"
    NO_FAULT_DETECTED = "No fault detected"
    IMAGE_CAPTURE_SUCCESS = "Image captured successfully"
    IMAGE_CAPTURE_FAILED = "Image capture failed"
