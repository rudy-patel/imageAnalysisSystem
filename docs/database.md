### Tables
#### `users`
| id  |  name | email  |  password | primary_camera |
|---|---|---|---|---|
|  the user id |  the user's name | the user's email  | the user's password  | this user's primary camera |

#### `event`
| id  |  user_id | camera_id  |  type | timestamp | name | image_link |
|---|---|---|---|---|---|---|
|  the event id |  the corresponding user id | the corresponding camera id  | the type of event/notification | the time at which this occurred | the name associated to this event (recognized face or shape) | AWS image link |

#### `camera`
| id  |  user_id | name  |  status | mode | last_heartbeat | 
|---|---|---|---|---|---|
|  the camera id |  the corresponding user id | the name of the camera | the current status of the camera (online/offline) | the current mode of the camera (facial/fault) | the last heartbeat received |

### Setup

#### SQL
For the server to communicate with the database the environment variable "DB_PASSWORD" must be set. This can be done using the "export" command on UNIX like systems or by following [this](https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0) guide on Windows.

#### Image Store
To access the S3 image storage AWS credentials must configured. This is done by placing a "config.txt" file and "credentials.txt" file in the "home/.aws/" directory. Contact bstolte@ualberta if you need these files. 

### Database updates
So you made a database schema change, how do you propagate that change to production?

Using `flask_migrate`, this is relatively easy:
1. From the root directory in your Python virtual environment, run `flask db migrate`
2. Then, run `flask db upgrade`

You're all set!