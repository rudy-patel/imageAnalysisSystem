import enum

class EventType(enum.Enum):
    FACIAL_MATCH_SUCCESS = "Face recognized"
    FACIAL_MATCH_FAILED = "New face detected"
    FACIAL_MATCH_ERROR = "Something went wrong"
    SHAPE_DETECT_SUCCESS = "Shape detected"
    NO_SHAPE_DETECTED = "No shape detected"
    IMAGE_CAPTURE_SUCCESS = "Image captured successfully"
    IMAGE_CAPTURE_FAILED = "Image capture failed"
