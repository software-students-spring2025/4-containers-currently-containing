# 🖐️ Hand Angle Detector (Docker + MediaPipe + Webcam Stream)

This project detects hand joint angles in real-time using [MediaPipe](https://mediapipe.dev/) and [OpenCV](https://opencv.org/), all running inside a Docker container.

It prints labeled joint angles (like `Thumb MCP→IP: 145.2°`) as you move your hand in front of your webcam. The webcam stream is served from your host machine using a lightweight Flask app.

---

## 📁 Project Structure

```
hand-angle-detector/
├── main.py              # Real-time hand angle detector (runs in Docker)
├── webcam_streamer.py   # Flask webcam streaming server (runs on host)
├── Dockerfile           # Python 3.11 + MediaPipe + OpenCV
└── README.md
```

---

## ✅ Requirements

- macOS or Linux
- Docker
- Python 3.10 or 3.11 on host
- `flask` and `opencv-python` on host for the webcam server

Install dependencies (for the host):
```bash
pip install flask opencv-python
```

---

## 🚀 How to Run

### 1. Start the webcam streamer (on your host)

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

---

## 🧠 How It Works

- MediaPipe detects 21 hand landmarks
- Angles between joints are calculated using vector geometry
- Output is updated in real time for the first detected hand

---

## 🐳 Why Docker?

- Zero setup: no Python environment needed
- Clean, reproducible environment for everyone
- Cross-platform support
