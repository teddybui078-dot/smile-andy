# Smile Andy — Checkpoints

Each checkpoint lives on its own branch, cut from the previous one (`main → a → b → c → d → e`).
When a checkpoint is reviewed and accepted: `git switch main && git merge --ff-only <branch> && git push`.
Session prompts and time caps come from `PLAN.md`. Hard cap per checkpoint: 15–20 min.

| CP | Branch | Adds | Done when |
|---|---|---|---|
| A | `checkpoint-a-setup` | venv, deps, model file, `.env`, setup check | `check_setup.py` prints PASS for camera, model, API key |
| B | `checkpoint-b-face-tracking-overlay` | `tracking.py`, `main.py`, `config.py` (Session 1) | live window shows landmarks + FPS; "No face detected" when away |
| C | `checkpoint-c-expression` | `expression.py` (Session 2) | label switches to HAPPY and SAD on purpose |
| D | `checkpoint-d-openai-cheer` | `cheer.py` (Session 3) | frown 3 s → message on screen and spoken |
| E | `checkpoint-e-polish-bugfix` | Sessions 4 + 5 (polish, then bug fixes only) | clean UI, all keys work, runs 5 min without crashing |

---

## A — Setup
- [ ] Status
- **Goal:** everything installed and proven working before any app code.
- **Files:** `requirements.txt`, `check_setup.py`, `models/face_landmarker.task` (not committed), `.env` (not committed)
- **Done when:** `.venv/bin/python check_setup.py` → camera PASS, model PASS, API key PASS
- **Verified / not verified:** _(fill in at end)_

## B — Face tracking + overlay
- [ ] Status
- **Goal:** mirrored webcam feed with MediaPipe landmarks drawn, FPS top-left. No expression logic.
- **Files:** `tracking.py`, `main.py`, `config.py`
- **Done when:** live window shows face landmarks + FPS; Q quits
- **Verified / not verified:** _(fill in at end)_

## C — Expression
- [ ] Status
- **Goal:** 3 s neutral calibration, blendshape scores, smoothing, hysteresis state machine (HAPPY / NEUTRAL / SAD), debug bars, C recalibrates.
- **Files:** `expression.py`, `config.py`, `main.py`
- **Done when:** you can make the label go HAPPY and SAD on purpose
- **Verified / not verified:** _(fill in at end)_

## D — OpenAI cheer
- [ ] Status
- **Goal:** SAD 3 s → chat message + TTS; HAPPY 3 s → short text; background thread, 30 s cooldown, fallback list.
- **Files:** `cheer.py`, `config.py`, `main.py`
- **Done when:** frown 3 s → message appears on screen and is spoken; video never freezes
- **Verified / not verified:** _(fill in at end)_

## E — Polish + bug fixes
- [ ] Status
- **Goal:** Session 4 polish (message panel, color-coded overlay, key hints, M mute, D debug) → **feature freeze** → Session 5 bug fixes only.
- **Files:** existing files only
- **Done when:** demo looks clean, all keys work, 5 min run with no crash
- **Verified / not verified:** _(fill in at end)_
