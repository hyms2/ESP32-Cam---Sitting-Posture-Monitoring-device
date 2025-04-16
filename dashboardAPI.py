# from flask import Flask, request, jsonify
# import cv2
# import numpy as np
# from ultralytics import YOLO
# import base64

# app = Flask(__name__)
# model = YOLO("yolov8n-pose.pt")

# def calculate_angle(p1, p2, p3):
#     a = np.array(p1)
#     b = np.array(p2)
#     c = np.array(p3)
#     ba = a - b
#     bc = c - b
#     cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
#     angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
#     return np.degrees(angle)

# def calculate_posture_score(keypoints):
#     if keypoints is None or len(keypoints[0]) < 14:
#         return 1, "Posture not detected", "Ensure your full body is visible to the camera."
#     try:
#         shoulder = keypoints[0][5]
#         hip = keypoints[0][11]
#         knee = keypoints[0][13]
#         angle = calculate_angle(shoulder, hip, knee)

#         if angle >= 160:
#             return 9, "Great posture!", "You're sitting upright — keep it up!"
#         elif 130 <= angle < 160:
#             return 6, "Moderate posture", "Try to sit a bit straighter."
#         else:
#             return 3, "Poor posture", "You may be slouching or leaning too far forward."
#     except Exception as e:
#         return 2, "Error analyzing pose", str(e)

# # Store latest result for Streamlit live updates
# latest_result = {}

# @app.route('/upload', methods=['POST'])
# def upload_image():
#     global latest_result
#     img_data = request.get_data()
#     if not img_data:
#         return jsonify({"error": "No image uploaded"}), 400

#     img_np = np.frombuffer(img_data, np.uint8)
#     img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

#     results = model(img)
#     keypoints = results[0].keypoints.xy.cpu().numpy() if results[0].keypoints else None
#     score, summary, tip = calculate_posture_score(keypoints)

#     img_with_kp = results[0].plot()
#     _, img_encoded = cv2.imencode('.jpg', img_with_kp)
#     img_bytes = img_encoded.tobytes()

#     base64_img = base64.b64encode(img_bytes).decode('utf-8')

#     latest_result = {
#         "score": score,
#         "summary": summary,
#         "tip": tip,
#         "image": base64_img
#     }

#     return jsonify(latest_result)

# @app.route('/latest', methods=['GET'])
# def get_latest():
#     if latest_result:
#         return jsonify(latest_result)
#     else:
#         return jsonify({"error": "No image yet"}), 404

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5000)

# app.py (Flask server with integrated posture AI scoring)

from flask import Flask, request, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import base64
import math

app = Flask(__name__)
model = YOLO("yolov8n-pose.pt")

# Scoring logic based on ergonomic posture guide
def calculate_angle(p1, p2, p3):
    a = np.array(p1)
    b = np.array(p2)
    c = np.array(p3)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def score_posture_from_keypoints(keypoints):
    if keypoints is None or len(keypoints[0]) < 17:
        return 1, "Posture not detected", "Ensure your full body is visible to the camera."

    kp = keypoints[0]
    NOSE = 0
    LEFT_SHOULDER = 5
    RIGHT_SHOULDER = 6
    LEFT_HIP = 11
    RIGHT_HIP = 12
    LEFT_KNEE = 13
    RIGHT_KNEE = 14
    LEFT_ANKLE = 15
    RIGHT_ANKLE = 16

    try:
        spine_angle_left = calculate_angle(kp[LEFT_SHOULDER], kp[LEFT_HIP], kp[LEFT_KNEE])
        spine_score = 9 if 150 <= spine_angle_left <= 180 else 6 if 120 <= spine_angle_left < 150 else 3

        hip_angle_left = calculate_angle(kp[LEFT_HIP], kp[LEFT_KNEE], kp[LEFT_ANKLE])
        pelvis_score = 9 if 120 <= hip_angle_left <= 135 else 6 if 100 <= hip_angle_left < 120 else 3

        shoulder_y_diff = abs(kp[LEFT_SHOULDER][1] - kp[RIGHT_SHOULDER][1])
        shoulder_score = 9 if shoulder_y_diff < 20 else 6 if shoulder_y_diff < 50 else 3

        shoulder_center = (kp[LEFT_SHOULDER] + kp[RIGHT_SHOULDER]) / 2
        head_alignment = abs(kp[NOSE][0] - shoulder_center[0])
        head_score = 9 if head_alignment < 20 else 6 if head_alignment < 60 else 3

        hip_y_diff = abs(kp[LEFT_HIP][1] - kp[RIGHT_HIP][1])
        symmetry_score = 9 if hip_y_diff < 20 else 6 if hip_y_diff < 50 else 3

        total_score = np.mean([
            spine_score,
            pelvis_score,
            shoulder_score,
            head_score,
            symmetry_score
        ])

        if total_score >= 8:
            summary = "Excellent ergonomic posture"
            tip = "Maintain this upright, balanced sitting position."
        elif total_score >= 5:
            summary = "Moderate posture"
            tip = "Consider adjusting your back, shoulders or head alignment."
        else:
            summary = "Poor posture"
            tip = "You're slouching or leaning — please correct your position."

        return round(total_score, 2), summary, tip

    except Exception as e:
        return 1, "Error in posture scoring", str(e)

# Store latest result for Streamlit live updates
latest_result = {}

@app.route('/upload', methods=['POST'])
def upload_image():
    global latest_result
    img_data = request.get_data()
    if not img_data:
        return jsonify({"error": "No image uploaded"}), 400

    img_np = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    results = model(img)
    keypoints = results[0].keypoints.xy.cpu().numpy() if results[0].keypoints else None
    score, summary, tip = score_posture_from_keypoints(keypoints)

    img_with_kp = results[0].plot()
    _, img_encoded = cv2.imencode('.jpg', img_with_kp)
    img_bytes = img_encoded.tobytes()

    base64_img = base64.b64encode(img_bytes).decode('utf-8')

    latest_result = {
        "score": score,
        "summary": summary,
        "tip": tip,
        "image": base64_img
    }

    return jsonify(latest_result)

@app.route('/latest', methods=['GET'])
def get_latest():
    if latest_result:
        return jsonify(latest_result)
    else:
        return jsonify({"error": "No image yet"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)