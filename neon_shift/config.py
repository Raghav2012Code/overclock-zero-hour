"""Central configuration for Overclock: Zero Hour.

All tuning constants live here so gameplay feel can be adjusted in one
place. Everything is frame-rate independent: speeds are px/sec and the
game loop integrates with a clamped ``dt``.
"""

from __future__ import annotations

TITLE = "Overclock: Zero Hour"
VERSION = "1.0.0"

# ---------------------------------------------------------------- window
WIDTH = 960
HEIGHT = 540
FPS = 60
# Clamp dt so tab-outs / hitches never teleport physics.
MAX_DT = 1.0 / 20.0

# ---------------------------------------------------------------- world
GROUND_Y = 452  # y of the track surface (player feet rest here)
GRAVITY = 2800.0  # px / s^2
JUMP_VELOCITY = -980.0  # initial jump impulse (px / s)
JUMP_CUT_MULTIPLIER = 0.45  # velocity kept when jump released early
COYOTE_TIME = 0.10  # grace period to jump after leaving ground (s)
JUMP_BUFFER = 0.14  # jump pressed slightly early still fires (s)
FAST_FALL_GRAVITY_MULT = 1.55  # extra gravity while holding DOWN in air

# ---------------------------------------------------------------- player
PLAYER_X = 150  # fixed screen x of the runner
PLAYER_W = 34
PLAYER_H = 64
PLAYER_SLIDE_H = 30  # hitbox height while sliding
PLAYER_RUN_ANIM_SPEED = 11.0  # leg cycle Hz at base speed

# ---------------------------------------------------------------- speed / difficulty
BASE_SPEED = 380.0  # world scroll px / s
MAX_SPEED = 860.0
SPEED_RAMP = 7.5  # px / s gained per second survived
SCORE_PER_SECOND = 10.0
CELL_BONUS = 25

# ---------------------------------------------------------------- spawner
SPAWN_MIN_GAP = 300.0  # px between hazard groups at start
SPAWN_MAX_GAP = 640.0
MIN_GAP_FLOOR = 210.0  # tightest gap at max difficulty
SPAWN_AHEAD = WIDTH + 120.0  # x where new hazards appear

# ---------------------------------------------------------------- colors (retro-cyberpunk palette)
BLACK = (8, 8, 18)
BG_TOP = (10, 6, 32)
BG_BOTTOM = (26, 8, 44)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 45, 149)
NEON_YELLOW = (255, 236, 39)
NEON_GREEN = (57, 255, 20)
NEON_ORANGE = (255, 110, 0)
NEON_PURPLE = (178, 102, 255)
WHITE = (235, 245, 255)
DIM = (120, 130, 160)
TRACK = (18, 20, 38)
TRACK_LINE = (0, 255, 255)

# ---------------------------------------------------------------- effects
SCREEN_SHAKE_MAGNITUDE = 14.0
SCREEN_SHAKE_DECAY = 60.0  # magnitude lost per second
PARTICLE_CAP = 420
GRID_HORIZON = 300  # horizon line for perspective grid floor

# ---------------------------------------------------------------- audio
AUDIO_ENABLED = True
AUDIO_FREQUENCY = 44100
AUDIO_BUFFER = 512
MASTER_VOLUME = 0.5

# ---------------------------------------------------------------- controls
KEY_JUMP = "SPACE / UP / W"
KEY_SLIDE = "DOWN / S"
KEY_RESTART = "R / SPACE"
KEY_QUIT = "ESC"
