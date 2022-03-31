from server.main import enum_to_string, camera_name_from_id
from server.models.models import Camera
import enum

class TestEnum(enum.Enum):
    TEST = "TEST_VALUE"

def test_enum_to_string():
    assert enum_to_string(TestEnum.TEST) == "TEST_VALUE"

def test_camera_name_from_id(test_client):
    test_cam_id = 6
    test_cam_name = Camera.query.filter_by(id=test_cam_id).first().name

    assert camera_name_from_id(test_cam_id) == test_cam_name