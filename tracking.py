import time

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

import config


class FaceTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        self.landmarker = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=config.MODEL_PATH),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            output_face_blendshapes=True))
        self.last_ms = 0

    def read(self):
        """Returns (frame, landmarks, blendshapes); frame is None if the camera fails,
        landmarks and blendshapes are None if no face is found."""
        ok, frame = self.cap.read()
        if not ok:
            return None, None, None
        frame = cv2.flip(frame, 1)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ms = max(int(time.monotonic() * 1000), self.last_ms + 1)  # VIDEO mode needs increasing timestamps
        self.last_ms = ms
        result = self.landmarker.detect_for_video(image, ms)
        if not result.face_landmarks:
            return frame, None, None
        blendshapes = {c.category_name: c.score for c in result.face_blendshapes[0]}
        return frame, result.face_landmarks[0], blendshapes

    def draw_overlay(self, frame, landmarks, color):
        h, w = frame.shape[:2]
        for lm in landmarks:
            cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), config.DOT_RADIUS, color, -1)
