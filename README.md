# Smile Andy

A webcam app that tracks your face, draws a wireframe overlay on it, works out whether you look happy, neutral or sad, and cheers you up with a message from OpenAI when you look down.

Built in 4 hours for a hackathon.

## Status

| Checkpoint | What it adds | State |
|---|---|---|
| A | Setup: environment, model, API key check | Done |
| B | Live face tracking + wireframe overlay on localhost | Done |
| C | Expression detection (happy / neutral / sad) | Next |
| D | OpenAI cheer-up messages + voice | Planned |
| E | Polish + bug fixes | Planned |

Details for each checkpoint are in [CHECKPOINTS.md](CHECKPOINTS.md).

## Setup

Needs Python 3.12 (MediaPipe does not support 3.14 yet) and a webcam.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p models && curl -L -o models/face_landmarker.task \
  https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
cp .env.example .env    # then add your OPENAI_API_KEY
.venv/bin/python check_setup.py    # should print PASS three times
```

## Run

```bash
.venv/bin/python main.py
```

Open http://localhost:8000. Press Ctrl+C in the terminal to stop it and turn off the camera.

On macOS, the first run asks for camera permission for your terminal or editor.

## How it works

- `tracking.py`: reads the webcam, finds the face with the MediaPipe Face Landmarker, and draws the wireframe.
- `main.py`: a Flask server that streams the annotated video to the browser.
- `config.py`: every tunable number (camera, port, overlay look).

## License

MIT, see [LICENSE](LICENSE).
