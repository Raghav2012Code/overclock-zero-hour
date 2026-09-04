# AGENTS.md — Overclock: Zero Hour

## Layout (flat root, no package)
`config.py`, `main.py`, `run.py` at root; `core/`, `entities/`, `graphics/`,
`ui/`, `tests/`. Imports are root-relative (`import config`,
`from core.game import Game`). Always run from the repo root; there is no
`neon_shift/` package anymore.

## Run / test
- Run: `python main.py` (or `python run.py`)
- Tests: `python -m unittest discover -s tests -t .` — the `-t .` is
  required because `tests/` is a package (`tests.support` imports fail
  without it). Stdlib only, ~33 tests, <1s.
- Dependency is `pygame-ce` (not `pygame` — classic pygame doesn't build
  on Python 3.14 here). Floor pinned in `requirements.txt`.
- CI (`.github/workflows/ci.yml`): compileall + tests on 3.11–3.13.

## Headless testing rules
- Every test module must set `SDL_VIDEODRIVER`/`SDL_AUDIODRIVER` to `dummy`
  **before** importing pygame or game code (`tests/support.py` pattern).
- `Game._poll_held_keys` calls `pygame.key.get_pressed()` — stub it with
  a lambda in tests and drive `slide_held` / `press_jump()` explicitly.
- `SoundBank` falls back to silent stubs when the mixer is unavailable;
  this is by design, not a failure.

## Pygame gotchas (verified the hard way)
- `KEYDOWN` events have **no `repeat` attribute** — use
  `getattr(event, "repeat", 0)`. Direct access crashes live play.
- Rendering must never mutate sim state: entity `draw()` methods take
  `ox, oy` shake offsets (`rect.move()` / locals). Don't reintroduce the
  nudge-and-restore pattern.
- `config.py` owns all tuning constants — put new knobs there, not inline.

## Shell
Windows PowerShell 5.1: chain with `; if ($?) { ... }` (no `&&`), filter
with `Select-Object -First/-Last` (no `tail`). Prefer dedicated file tools
over shell for reading/editing.

## Workflow
Commit after each logical change (checkpoints for later). Never commit
`__pycache__/` or `overclock_hiscore.txt` (both gitignored). Verify with
compileall + the unittest suite before committing.
