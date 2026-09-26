import os

import cv2
from dotenv import load_dotenv
from mediapipe.tasks.python import BaseOptions, vision

cap = cv2.VideoCapture(0)
ok = cap.read()[0]
cap.release()
print('camera ', 'PASS' if ok else 'FAIL (check macOS camera permission for your terminal)')

try:
    vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path='models/face_landmarker.task'),
        output_face_blendshapes=True))
    print('model  ', 'PASS')
except Exception as e:
    print('model  ', f'FAIL ({e})')

load_dotenv()
print('api key', 'PASS' if os.getenv('OPENAI_API_KEY') else 'FAIL (put OPENAI_API_KEY in .env)')
