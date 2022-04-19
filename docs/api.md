### API documentation
The API is made with Python and Flask. The following routes have been defined below:

#### `GET /heartbeat/<int:camera_id>`
Returns camera configuration values from the server

**Response**:
```json
{
    "camera_id": "<int>",
    "mode": "<string>",
    "is_primary": "<bool>",
    "encodings_hash": "<int>",
}
```

#### `/make_primary/<int:camera_id>`
Makes the passed in camera id the primary camera for the current user

**Response**: redirect to **cameras** page

#### `POST /<int:camera_id>/facial-detection-event"`
Registers a new facial detection event and returns success/failure of operation

**Response**:
```json
{
    "success": "<bool>",
}
```

#### `POST /<int:camera_id>/ring-shape-analysis-event"`
Registers a new shape detection event and returns success/failure of operation

**Response**:
```json
{
    "success": "<bool>",
}
```

#### `GET /video_feed/<int:primary_camera>"`
Returns the generated frame from the livestream of the primary camera

**Response**:
```json
{
    "Content-Type": "image/jpeg<string>",
}
```

