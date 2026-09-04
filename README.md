# Overclock: Zero Hour

A complete, modular, production-ready 2D endless runner in Pygame
(pygame-ce) with a retro-cyberpunk theme. 100% procedural graphics and
synthesized SFX — no external images or audio files.

You are a runner jacked into a neon grid at midnight. Dodge spikes,
slide under beams, thread patrol drones, and grab energy cells while
the city accelerates around you.

## Quick start

Requirements: Python 3.10+.

```bash
pip install -r requirements.txt
python main.py
# or
python run.py
```

## Testing

Headless suite, stdlib only (33 tests, <1s):

```bash
python -m unittest discover -s tests -t .
```

Run from the repo root (imports are root-relative). The `-t .` is
required because `tests/` is a package.

Covers jump/coyote/buffer/slide physics, frame-rate independence,
collision forgiveness, hazard lethality, spawner bounds and variety,
state transitions, input handling, hi-score persistence, and render
purity. CI (`.github/workflows/ci.yml`) runs compile + tests on
Python 3.11–3.13 for every push and PR.

## Controls

| Input | Action |
| --- | --- |
| SPACE / UP / W | Jump (release early = short hop) |
| DOWN / S | Slide — cuts hitbox; dive-falls while airborne |
| P | Pause |
| SPACE / ENTER / UP | Start from menu |
| R / SPACE / ENTER | Reboot after flatline |
| M | Back to menu after flatline |
| ESC | Quit |

## Hazards & pickups

- **Ground spikes** — jump them (singles early, doubles later).
- **Overhead beams** — slide under them; chevrons mark the gap.
- **Patrol drones** — oscillating hover; slide under high ones, jump low ones.
- **Energy cells** — +25 score each with particle bursts and a chime.

## Game feel

- Frame-rate independent physics (`dt`, clamped against hitches).
- Variable jump cut, coyote time (0.10s), jump buffering (0.14s).
- Difficulty ramp: scroll speed 380 → 860 px/s with tighter spawn gaps over ~90s.
- Forgiving hitboxes, screen shake + red flash on crash, pooled particles
  (run trails, landing dust, pickup sparkles, crash explosion).
- Multi-layer parallax city, synthwave sun, perspective grid floor.
- Cyberpunk telemetry HUD (score, best, cells, velocity gauge, FPS) with CRT scanlines.
- Hi-score persisted to `overclock_hiscore.txt`; synthesized SFX with silent
  fallback when no audio device is present.

## Project layout

All game code lives in the root folder:

```text
config.py        # all tuning constants (physics, speed, colors, audio)
main.py          # entry point (python main.py)
run.py           # convenience launcher (python run.py)
core/            # game loop, state machine, spawner, collision, audio synth
entities/        # player, hazards, pickups, particles
graphics/        # parallax background, neon fx, procedural sprite factory
ui/              # telemetry HUD, start / game-over / pause screens
tests/           # headless unittest suite (+ support.py helpers)
AGENTS.md        # contributor notes for AI coding agents
```

## Tuning

Open `config.py` — every feel parameter (gravity, jump velocity, coyote
time, buffer, slide height, speed ramp, spawn gaps, shake, volumes) is a
named constant in one place.
