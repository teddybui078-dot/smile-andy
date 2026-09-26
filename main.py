import threading
import time

import cv2
from flask import Flask, Response

import config
from tracking import FaceTracker

app = Flask(__name__)
tracker = FaceTracker()
lock = threading.Lock()  # one camera + increasing VIDEO timestamps: only one reader at a time

PAGE = '''<!doctype html>
<title>Smile Andy</title>
<body style="margin:0;background:#111;display:flex;justify-content:center;align-items:center;height:100vh">
<img src="/video" style="max-width:100%;max-height:100vh">
</body>'''


def frames():
    last = time.time()
    while True:
        with lock:
            frame, landmarks, _ = tracker.read()
        if frame is None:
            time.sleep(0.1)
            continue
        if landmarks:
            tracker.draw_overlay(frame, landmarks, config.OVERLAY_COLOR)
        else:
            cv2.putText(frame, 'No face detected', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        now = time.time()
        fps = 1 / max(now - last, 1e-6)
        last = now
        cv2.putText(frame, f'FPS {fps:.0f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        ok, jpg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, config.JPEG_QUALITY])
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n'


@app.route('/')
def index():
    return PAGE


@app.route('/video')
def video():
    return Response(frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    print(f'Open http://localhost:{config.PORT}')
    app.run(host='127.0.0.1', port=config.PORT, threaded=True)
