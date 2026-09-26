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
        """Sparse face wireframe (key points joined by straight lines) plus corner brackets."""
        h, w = frame.shape[:2]
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        for a, b in WIREFRAME_EDGES:
            cv2.line(frame, pts[a], pts[b], color, config.LINE_THICKNESS, cv2.LINE_AA)
        for i in {i for edge in WIREFRAME_EDGES for i in edge}:
            cv2.circle(frame, pts[i], config.NODE_RADIUS, color, 1, cv2.LINE_AA)

        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        pad = int(config.BRACKET_PAD * (max(xs) - min(xs)))
        x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
        n = (x1 - x0) // 6
        for x, y, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            cv2.line(frame, (x, y), (x + dx * n, y), color, config.BRACKET_THICKNESS)
            cv2.line(frame, (x, y), (x, y + dy * n), color, config.BRACKET_THICKNESS)


# MediaPipe Face Mesh indices. Forehead 103/332, face edge 234/454 (cheek) and 172/397 (jaw),
# chin 148/377, eyes outer 33/263, inner 133/362, lower lid 145/374, nose bridge 168, tip 1,
# nostrils 98/327, mouth corners 61/291, upper lip 0, lower lip 17.
WIREFRAME_EDGES = [
    (103, 332), (103, 234), (332, 454), (103, 33), (332, 263),         # forehead + outer frame
    (234, 33), (454, 263),                                           # cheek edge to eyes
    (33, 145), (145, 133), (133, 33), (263, 374), (374, 362), (362, 263),  # eyes
    (133, 168), (168, 362), (133, 1), (362, 1),                      # bridge + nose V
    (234, 1), (454, 1), (1, 98), (1, 327), (98, 327),                # cheeks + nose base
    (98, 61), (327, 291), (61, 0), (0, 291), (61, 17), (17, 291),    # mouth
    (234, 172), (454, 397), (172, 61), (397, 291),                   # jaw to mouth line
    (172, 148), (397, 377), (148, 377),                              # chin
]
