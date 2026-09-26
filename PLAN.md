# CLAUDE.md — Cheer-Up Cam (4-hour hackathon)

## What this project is
A webcam app that tracks the user's face, overlays face landmarks, detects
whether they look HAPPY, NEUTRAL, or SAD, and when they look sad it
generates a short cheer-up message with the OpenAI API (shown on screen and
spoken aloud).

## Rules for the agent (read every session)
- **Each session has ONE goal and a hard cap of 15–20 minutes.** Only work on
  the current session's goal. Do not start the next session's work.
- **Do not refactor, rename, or "improve" code outside the current goal.**
- Prefer the simplest thing that works. This is a demo, not a product.
- Keep all tunable numbers (thresholds, cooldowns, timings) in `config.py`.
- Never hardcode the API key. Read `OPENAI_API_KEY` from `.env` via `python-dotenv`.
- The video loop must never block. Any network call runs in a background thread.
- At the end of the session, tell the user exactly how to run and test what you built.

## Tech stack
- Python 3.10+
- `opencv-python` — webcam capture and drawing
- `mediapipe` — Face Landmarker (478 landmarks + face blendshapes)
- `openai` — chat completion for messages, text-to-speech for voice
- `python-dotenv` — load API key
- Audio playback: `pygame` (simplest cross-platform option)

## File layout
```
main.py          # app loop: ties modules together, UI text, key handling
tracking.py      # live tracking: webcam capture, Face Landmarker, landmark overlay
expression.py    # calibration, scoring, smoothing, state machine
cheer.py         # OpenAI text + TTS, cooldown, fallback messages
config.py        # all thresholds and timings
models/face_landmarker.task
.env             # OPENAI_API_KEY=...
requirements.txt
```

---

## Timeline (4 hours total)

| Time | Block | Cap |
|---|---|---|
| 0:00–0:15 | Setup (human, no AI) | 15 min |
| 0:15–0:35 | **Session 1:** Face tracking + overlay | 20 min |
| 0:35–0:45 | Human: test, commit | 10 min |
| 0:45–1:05 | **Session 2:** Expression detection | 20 min |
| 1:05–1:25 | Human: tune thresholds by hand, commit | 20 min |
| 1:25–1:45 | **Session 3:** OpenAI features | 20 min |
| 1:45–2:00 | Human: test full flow, commit | 15 min |
| 2:00–2:20 | **Session 4:** Check + polish | 20 min |
| 2:20 | **FEATURE FREEZE** | — |
| 2:20–2:40 | **Session 5:** Bug fixes only | 20 min |
| 2:40–3:20 | Buffer (only for catching up — no new features) | 40 min |
| 3:20–4:00 | README, record backup demo video, rehearse pitch | 40 min |

### Setup checklist (human, before Session 1)
- [ ] `git init`, create venv, `pip install opencv-python mediapipe openai python-dotenv pygame`
- [ ] Download `face_landmarker.task` from the MediaPipe docs into `models/`
- [ ] Create `.env` with `OPENAI_API_KEY=...` and add `.env` to `.gitignore`
- [ ] Confirm webcam works: `python -c "import cv2; print(cv2.VideoCapture(0).read()[0])"` prints `True`

---

## Session prompts

### Session 1 — Face tracking + overlay (20 min)
```
Build tracking.py, main.py, and config.py.
tracking.py: a FaceTracker class that opens the webcam with OpenCV, runs
MediaPipe Face Landmarker in VIDEO mode with output_face_blendshapes=True
(using models/face_landmarker.task), and for each frame returns the mirrored
frame, the landmarks, and the blendshapes as a {name: score} dict (or None
if no face). It also has a draw_overlay(frame, landmarks, color) method that
draws the landmarks as small dots.
main.py: the app loop. Get each frame from FaceTracker, draw the overlay,
show FPS in the top-left corner, show "No face detected" when there's no
face. Press Q to quit.
Do NOT add any expression logic yet.
```
**Done when:** live window shows your face with landmarks and an FPS counter.

### Session 2 — Expression detection (20 min)
```
Create expression.py and hook it into main.py. It reads the blendshapes
dict from FaceTracker in tracking.py.
1. Calibration: for the first 3 seconds, show "Calibrating - keep a neutral
   face" and record the average of each blendshape as the baseline.
2. Scoring, relative to baseline:
   happy_score = avg(mouthSmileLeft, mouthSmileRight) + 0.3 * avg(eyeSquintLeft, eyeSquintRight)
   sad_score   = avg(mouthFrownLeft, mouthFrownRight) + 0.5 * browInnerUp
3. Smooth both scores with a rolling average over ~1.5 seconds.
4. State machine with hysteresis (separate enter/exit thresholds) so the
   label doesn't flicker: HAPPY, NEUTRAL, SAD.
5. Draw the state label and two small horizontal debug bars for the scores.
6. Press C to recalibrate.
Put all thresholds and window sizes in config.py.
```
**Done when:** you can make the label switch to HAPPY and SAD on purpose.

### Session 3 — OpenAI features (20 min)
```
Create cheer.py and hook it into main.py.
1. When state has been SAD for 3 continuous seconds, call the OpenAI chat
   API (use a small, cheap model) for a warm, 1-2 sentence cheer-up message.
2. Convert that message to speech with the OpenAI text-to-speech endpoint,
   save it to a temp mp3, and play it with pygame.
3. When state has been HAPPY for 3 seconds, generate a short positive
   message (text only, no voice).
4. All API calls run in a background thread. The video loop must never freeze.
5. 30-second cooldown between messages (value in config.py).
6. If any API call fails, use a random message from a hardcoded fallback list
   of 8 cheer-up lines and skip the voice.
7. Show the latest message as text on the video frame.
```
**Done when:** frown for 3 seconds → message appears on screen and is spoken.

### Session 4 — Check + polish (20 min)
```
First, check: read through main.py, tracking.py, expression.py, cheer.py and list any
obvious problems (crashes on no face, thread issues, missing error handling).
Fix only the quick ones. Then polish the UI only:
- Clean semi-transparent message panel at the bottom of the frame with
  wrapped text
- Color-coded face overlay: green = HAPPY, blue = SAD, gray = NEUTRAL
- Small key-hint line: "Q quit  C recalibrate  M mute"
- M toggles voice mute
- Hide debug bars unless D is pressed
No new features beyond this list.
```
**Done when:** the demo looks clean and all keys work.

### Session 5 — Bug fixes only (20 min)
```
Fix bugs only. Do not add features, change the UI, or refactor.
Here are the bugs I found:
[paste errors / describe what goes wrong and how to reproduce]
```
**Done when:** the app runs for 5 minutes straight without crashing.

---

## Staying on schedule
1. **Set a real timer for every session.** When it goes off, stop the agent
   and commit whatever works.
2. **At the 15-minute mark**, if the goal isn't close, cut scope (see below).
3. **Commit after every session:** `git commit -am "session N: <what works>"`
4. If a session goes badly, `git checkout .` back to the last commit rather
   than debugging for 20 more minutes.

## Cut list (drop in this order if behind)
1. Happy-state positive message
2. Hotkeys (C / M / D)
3. Text-to-speech (text on screen is still a full demo)
4. Eye-squint and brow weighting (mouth corners alone are enough)

**Never cut:** calibration, smoothing, fallback messages. These keep the
live demo from falling apart.

## Stretch goals (only if everything is done)
- Send the cheer-up message as a real SMS via Twilio
- Mood timeline graph shown when you quit
