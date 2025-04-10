# main.py
import cv2
import time
import mediapipe as mp
import numpy as np
from angle_api import latest_angles, angle_lock
from threading import Thread
from flask import Flask

def run_api():
    from angle_api import app
    app.run(host="0.0.0.0", port=5050)



def calculate_angle(a, b, c):
    """
    Calculate the angle (in degrees) between points a, b, and c.
    a, b, c are Mediapipe landmark objects (with x, y, z attributes).
    """
    a = np.array([a.x, a.y, a.z])
    b = np.array([b.x, b.y, b.z])
    c = np.array([c.x, c.y, c.z])
    
    ba = a - b
    bc = c - b

    # Clip the dot-product value to avoid numerical errors outside the range [-1,1]
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def extract_hand_angles(landmarks):
    """
    Given the 21 hand landmarks, return a list of angles
    for each relevant finger joint.
    """
    angles = []
    # Thumb
    angles.append(calculate_angle(landmarks[1], landmarks[2], landmarks[3]))
    angles.append(calculate_angle(landmarks[2], landmarks[3], landmarks[4]))
    # Index finger
    angles.append(calculate_angle(landmarks[5], landmarks[6], landmarks[7]))
    angles.append(calculate_angle(landmarks[6], landmarks[7], landmarks[8]))
    # Middle finger
    angles.append(calculate_angle(landmarks[9], landmarks[10], landmarks[11]))
    angles.append(calculate_angle(landmarks[10], landmarks[11], landmarks[12]))
    # Ring finger
    angles.append(calculate_angle(landmarks[13], landmarks[14], landmarks[15]))
    angles.append(calculate_angle(landmarks[14], landmarks[15], landmarks[16]))
    # Pinky
    angles.append(calculate_angle(landmarks[17], landmarks[18], landmarks[19]))
    angles.append(calculate_angle(landmarks[18], landmarks[19], landmarks[20]))
    return angles

if __name__ == "__main__":
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils

    # Replace with your own video source if necessary
    cap = cv2.VideoCapture(0)

    
    print("Starting real-time hand angle detection...")

    Thread(target=run_api, daemon=True).start()

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            # Frame not read properly; possibly end of stream
            break

        # Flip the frame horizontally so it mirrors the user's movement
        image = cv2.flip(image, 1)

        # Convert the frame from BGR to RGB (MediaPipe expects RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # If a hand is detected, extract the angles and print them
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                angles = extract_hand_angles(hand_landmarks.landmark)

                with angle_lock:
                    latest_angles.clear()
                    latest_angles.extend(angles)

                labels = [
                    "Thumb MCP→IP", "Thumb IP→Tip",
                    "Index MCP→PIP", "Index PIP→DIP",
                    "Middle MCP→PIP", "Middle PIP→DIP",
                    "Ring MCP→PIP", "Ring PIP→DIP",
                    "Pinky MCP→PIP", "Pinky PIP→DIP"
                ]

                print("🖐️ Hand Angles:")
                for label, angle in zip(labels, angles):
                    print(f"{label}: {angle:.2f}°")
                print("-" * 40)
        else:
            # No hand detected → set angles to None
            with angle_lock:
                latest_angles.clear()
                latest_angles.extend([None] * 10)

        
        # Optional small delay to avoid pegging the CPU
        time.sleep(0.01)

    cap.release()
    print("Finished.")
    
