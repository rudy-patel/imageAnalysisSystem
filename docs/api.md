### API documentation
The API is made with Python and Flask. The existing routes have been defined below:

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

**Response**: Flask response with the current live frame

#### `GET/POST /"`
Returns the home page HTML template

**Response**: home page HTML

#### `GET/POST /home"`
Returns the home page HTML template

**Response**: home page HTML

#### `GET/POST /login"`
Returns the login page HTML template

**Response**: login page HTML

#### `GET/POST /signup"`
Returns the signup page HTML template

**Response**: signup page HTML

#### `GET/POST /logout"`
Logs out the current user and redirects to login page

**Response**: login page HTML

#### `GET/POST /events"`
Returns the events page HTML template

**Response**: events page HTML

#### `GET/POST /view_event/<int:event_id>"`
Returns the view event page HTML template populated with the specified event

**Response**: view event page HTML

#### `GET/POST /cameras"`
Returns the cameras page HTML template

**Response**: cameras page HTML

#### `GET/POST /train"`
Returns the train page HTML template

**Response**: train page HTML

#### `GET /download/<int:event_id>"`
Returns the image associated with the specified event

**Response**: Flask response with image associated with the specified event