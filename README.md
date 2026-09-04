# Overclock: Zero Hour

A complete, modular, production-ready 2D endless runner in Pygame
(pygame-ce) with a retro-cyberpunk theme. 100% procedural graphics and
synthesized SFX — no external images or audio files.

## Run

```bash
pip install -r requirements.txt
python -m neon_shift.main
# or
python run.py
```

## Controls

| Input | Action |
| --- | --- |
| SPACE / UP / W | Jump (release early = short hop) |
| DOWN / S | Slide (cuts hitbox; dive-falls in air) |
| P | Pause |
| R / SPACE | Reboot after flatline |
| M | Back to menu after flatline |
| ESC | Quit |

## Hazards & pickups

- **Ground spikes** — jump them.
- **Overhead beams** — slide under them.
- **Patrol drones** — oscillating hover; time your jump/slide.
- **Energy cells** — +25 score each with particle bursts.

## Feel tech

- Frame-rate independent physics (`dt`, clamped).
- Variable jump cut, coyote time (0.10s), jump buffering (0.14s).
- Difficulty ramp: scroll speed + tighter spawn gaps over ~90s.
- Forgiving hitboxes, screen shake + red flash on crash, pooled particles.
- Multi-layer parallax city, synthwave sun, perspective grid floor.

## Layout

```text
neon_shift/
  config.py        # all tuning constants
  main.py          # entry point
  core/            # game loop, state, spawner, collision, audio synth
  entities/        # player, hazards, pickups, particles
  graphics/        # parallax background, neon fx, sprite factory
  ui/              # telemetry HUD, start / game-over / pause screens
```
