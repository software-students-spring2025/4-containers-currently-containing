![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![ML Client - CI](https://github.com/software-students-spring2025/4-containers-currently-containing/actions/workflows/ml-client.yml/badge.svg)
![Web App - CI](https://github.com/software-students-spring2025/4-containers-currently-containing/actions/workflows/web-app.yml/badge.svg)

# Containerized App Exercise

# Hand Gesture Authentication System

A containerized application that uses hand gesture recognition for secure document access. The system recognizes and authenticates users based on the angles between their finger joints.

## Team Members
- [Andy Cabindol](https://github.com/andycabindol)
- [David Yu](https://github.com/DavidYu00)
- [Jason Mai](https://github.com/JasonMai233)
- [Cyryl Zhang](https://github.com/nstraightbeam)

## System Overview

This system consists of three containerized components:

1. **Machine Learning Client** - Captures hand poses from a camera and calculates joint angles
2. **Web Application** - Provides user interface for registration, authentication, and document management
3. **MongoDB Database** - Stores user data, gesture passwords, and protected documents

The system uses angle-based authentication instead of traditional passwords. Users register by capturing the specific angles of their hand joints, and then authenticate by reproducing a similar hand gesture. 

## Database Structure

The MongoDB database consists of the following collections:

1. **users** - Stores user account information
   - Username, email, and creation timestamp
   - References to gesture passwords and owned documents

2. **gesture_passwords** - Stores gesture authentication data
   - 10 finger joint angles that form the "password"
   - Confidence threshold for authentication
   - Links to the user who created the gesture

3. **documents** - Stores protected documents
   - Document content and metadata
   - Access control based on user ownership
   - Tracks document creation and modification dates

4. **authentication_logs** - Records authentication attempts
   - Tracks successful and failed authentication attempts
   - Stores confidence levels for gesture recognition
   - Records device information and timestamps

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Webcam for hand gesture detection
- Git

### Running the System

1. Clone the repository:
```bash
git clone https://github.com/software-students-spring2025/4-containers-currently-containing.git
cd 4-containers-currently-containing
```

2. Start the webcam streamer (on your host)
cd into machine learning client dir
```bash
cd machine-learning-client
```
start webcam streaming
```bash
python webcam_streamer.py
```

This will start a webcam MJPEG stream at `http://localhost:8554`.

3. Start all services with Docker Compose:
```bash
docker compose up -d
```

4. Access the web application:
```bash
http://localhost:5055
```

### Running Individual Components

MongoDB Database 
```bash
docker compose up -d mongodb
```

Web Application
```bash
docker compose up -d web-app
```

Machine Learning Client
```bash
docker compose up -d ml-client
```

### Development

To test the database connection:
```bash
cd web-app
python3 test_db.py
```

To test the angle authentication system:
```bash
cd web-app
python3 test_angle_auth.py
```

To test the API endpoints:
```bash
cd web-app
python3 test_api.py
```


### Running the Hand Detector

Install dependencies (for the host):
```bash
pip install flask opencv-python
```

---

## 🚀 How to Run

### 1. Start the webcam streamer (on your host)

cd machine-learning-client

```bash
python webcam_streamer.py
```

This will start a webcam MJPEG stream at `http://localhost:8554`.

### 2. Build the Docker container

```bash
docker build -t hand-angle-detector .
```

### 3. Run the container

```bash
docker run -it hand-angle-detector
```

You should see hand joint angle outputs like:

```
🖐️ Hand Angles:
Thumb MCP→IP: 149.84°
Thumb IP→Tip: 147.75°
...
```
