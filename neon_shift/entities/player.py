"""Player: frame-rate independent run / jump / slide controller.

Features:
- gravity + variable jump cut (release SPACE early => shorter hop)
- coyote time + jump input buffering for forgiving controls
- slide cuts the hitbox height and adds fast-fall while airborne
- run-trail particles + landing dust hooks via ``ParticleSystem``
"""

from __future__ import annotations

import pygame

from neon_shift import config


class Player:
    def __init__(self) -> None:
        self.x = float(config.PLAYER_X)
        self.y = float(config.GROUND_Y - config.PLAYER_H)  # top-left y
        self.vy = 0.0
        self.grounded = True
        self.sliding = False
        self.slide_timer = 0.0
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.jump_held = False
        self.anim_time = 0.0
        self.run_trail_acc = 0.0
        self.dead = False

    # -- lifecycle ---------------------------------------------------------
    def reset(self) -> None:
        self.__init__()

    # -- hitbox --------------------------------------------------------------
    @property
    def width(self) -> float:
        return float(config.PLAYER_W + (10 if self.sliding else 0))

    @property
    def height(self) -> float:
        return float(config.PLAYER_SLIDE_H if self.sliding else config.PLAYER_H)

    @property
    def rect(self) -> pygame.Rect:
        """Current hitbox rect (bottom-aligned so slides hug the track)."""
        h = self.height
        w = self.width
        bottom = self.y + config.PLAYER_H if self.grounded and self.sliding else self.y + h
        # When standing/jumping, top-left y is authoritative.
        if not (self.grounded and self.sliding):
            return pygame.Rect(int(self.x), int(self.y), int(w), int(h))
        # Sliding on ground: pin feet to the track.
        return pygame.Rect(int(self.x), int(config.GROUND_Y - h), int(w), int(h))

    @property
    def center(self) -> tuple[float, float]:
        r = self.rect
        return (r.centerx, r.centery)

    # -- input ---------------------------------------------------------------
    def press_jump(self) -> None:
        """Queue a jump (buffered so slightly-early presses still fire)."""
        self.jump_buffer = config.JUMP_BUFFER
        self.jump_held = True

    def release_jump(self) -> None:
        """Variable jump cut: releasing early truncates upward velocity."""
        self.jump_held = False
        if not self.grounded and self.vy < 0.0:
            self.vy *= config.JUMP_CUT_MULTIPLIER

    def set_slide(self, held: bool) -> None:
        self.sliding = held
        if held:
            self.slide_timer += 0  # timer handled in update

    # -- physics ---------------------------------------------------------------
    def _try_consume_jump(self, particles) -> bool:
        if self.jump_buffer > 0.0 and (self.grounded or self.coyote > 0.0):
            self.vy = config.JUMP_VELOCITY
            self.grounded = False
            self.coyote = 0.0
            self.jump_buffer = 0.0
            self.sliding = False
            particles.trail(self.x, config.GROUND_Y - 4, config.NEON_CYAN, count=6)
            return True
        return False

    def update(self, dt: float, particles, slide_held: bool = False, sound=None) -> None:
        if self.dead:
            return
        was_grounded = self.grounded
        self.sliding = bool(slide_held and self.grounded)
        if slide_held and not self.grounded:
            # Air-slide => fast fall + dive feel.
            self.sliding = True

        self.jump_buffer = max(0.0, self.jump_buffer - dt)
        self.coyote = max(0.0, self.coyote - dt)

        jumped = self._try_consume_jump(particles)
        if jumped and sound is not None:
            sound.play_jump()

        # Gravity (extra pull while dive-holding DOWN in the air).
        g = config.GRAVITY
        if slide_held and not self.grounded:
            g *= config.FAST_FALL_GRAVITY_MULT
        # Higher gravity on the way down gives a snappy arc.
        if self.vy > 0.0:
            g *= 1.25
        self.vy += g * dt
        self.y += self.vy * dt

        floor_y = config.GROUND_Y - (config.PLAYER_SLIDE_H if self.sliding and self.grounded else config.PLAYER_H)
        # In-air slide uses the standing height for landing math.
        land_line = config.GROUND_Y - config.PLAYER_H
        if self.y >= land_line:
            self.y = land_line
            if not was_grounded and self.vy > 500.0:
                particles.land_dust(self.x + config.PLAYER_W / 2, config.GROUND_Y)
            self.vy = 0.0
            self.grounded = True
            self.coyote = config.COYOTE_TIME
        else:
            if was_grounded:
                # Just walked off... (no ledges in runner; kept for coyote correctness)
                self.coyote = config.COYOTE_TIME
            self.grounded = False

        if self.grounded:
            self.coyote = config.COYOTE_TIME

        # Run-cycle + trail emission.
        self.anim_time += dt
        if self.grounded:
            self.run_trail_acc += dt
            interval = 0.09
            if self.sliding:
                interval = 0.03
            while self.run_trail_acc >= interval:
                self.run_trail_acc -= interval
                particles.trail(
                    self.x + 4, config.GROUND_Y - 6,
                    config.NEON_MAGENTA if self.sliding else config.NEON_CYAN,
                )
        _ = floor_y  # (kept explicit for readability of landing math)

    # -- draw -------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, sprites: dict) -> None:
        r = self.rect
        if self.sliding:
            img = sprites["player_slide"]
        elif not self.grounded:
            img = sprites["player_jump"] if self.vy < 0 else sprites["player_fall"]
        else:
            # 2-frame run cycle scaled with world speed feel.
            phase = (self.anim_time * config.PLAYER_RUN_ANIM_SPEED) % 2.0
            img = sprites["player_run1"] if phase < 1.0 else sprites["player_run2"]
        surface.blit(img, (r.x + (self.width - img.get_width()) / 2 - 5, r.y + (r.height - img.get_height())))
