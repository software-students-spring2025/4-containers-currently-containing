from flask import Flask, jsonify
from threading import Lock
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
latest_angles = []
angle_lock = Lock()

@app.route("/hand-angles", methods=["GET"])
def get_hand_angles():
    with angle_lock:
        hand_present = all(a is not None for a in latest_angles)
        return jsonify({
            "hand_present": int(hand_present),
            "angles": latest_angles
        })
