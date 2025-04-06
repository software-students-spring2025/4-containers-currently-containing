import cv2
import mediapipe as mp
import numpy as np

def calculate_angle(a, b, c):
    a = np.array([a.x, a.y, a.z])
    b = np.array([b.x, b.y, b.z])
    c = np.array([c.x, c.y, c.z])
    
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))


def extract_hand_angles(landmarks):
    angles = []
    # Thumb
    angles.append(calculate_angle(landmarks[1], landmarks[2], landmarks[3]))
    angles.append(calculate_angle(landmarks[2], landmarks[3], landmarks[4]))
    # Index
    angles.append(calculate_angle(landmarks[5], landmarks[6], landmarks[7]))
    angles.append(calculate_angle(landmarks[6], landmarks[7], landmarks[8]))
    # Middle
    angles.append(calculate_angle(landmarks[9], landmarks[10], landmarks[11]))
    angles.append(calculate_angle(landmarks[10], landmarks[11], landmarks[12]))
    # Ring
    angles.append(calculate_angle(landmarks[13], landmarks[14], landmarks[15]))
    angles.append(calculate_angle(landmarks[14], landmarks[15], landmarks[16]))
    # Pinky
    angles.append(calculate_angle(landmarks[17], landmarks[18], landmarks[19]))
    angles.append(calculate_angle(landmarks[18], landmarks[19], landmarks[20]))
    return angles

def match_gesture(stored, live, threshold=10):
    return all(abs(s - l) < threshold for s, l in zip(stored, live))


# --- MediaPipe + Webcam ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

stored_gesture = None

print("👋 Press [SPACE] to store hand gesture.")
print("🔐 Press [ENTER] to verify against saved gesture.")
print("⎋ Press [ESC] to exit.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # get angles
        angles = extract_hand_angles(hand_landmarks.landmark)

        key = cv2.waitKey(5) & 0xFF
        if key == 27:  # esc
            break
        elif key == 32:  # space
            stored_gesture = angles
            print("✅ Gesture saved.")
        elif key == 13:  # this is the enter key
            if stored_gesture:
                match = match_gesture(stored_gesture, angles)
                print("✅ Match!" if match else "❌ No match.")
            else:
                print("⚠️ No gesture saved yet.")

    cv2.imshow("Gesture Password", image)

cap.release()
cv2.destroyAllWindows()
