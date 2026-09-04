"""Game orchestrator: loop, scoring, collisions, shake, state flow."""

from __future__ import annotations

import logging
import os
import random

import pygame

import config
from core.audio import SoundBank
from core.collision import collides
from core.spawner import Spawner
from core.state import GameState
from entities.particles import ParticleSystem
from entities.pickups import EnergyCell
from entities.player import Player
from graphics.background import ParallaxBackground
from graphics.sprites import build_sprites
from ui.hud import HUD
from ui.screens import Screens

HI_SCORE_FILE = "overclock_hiscore.txt"

logger = logging.getLogger(__name__)


def load_hi_score() -> int:
    try:
        if os.path.exists(HI_SCORE_FILE):
            with open(HI_SCORE_FILE, "r", encoding="utf-8") as fh:
                return max(0, int(fh.read().strip() or "0"))
    except (OSError, ValueError) as exc:
        logger.debug("could not load hi-score: %s", exc)
    return 0


def save_hi_score(value: int) -> None:
    try:
        with open(HI_SCORE_FILE, "w", encoding="utf-8") as fh:
            fh.write(str(int(value)))
    except OSError as exc:
        logger.debug("could not save hi-score: %s", exc)


class Game:
    """Owns the full runner simulation and rendering."""

    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.state = GameState.START
        self.sound = SoundBank()
        self.background = ParallaxBackground()
        self.player = Player()
        self.particles = ParticleSystem()
        self.spawner = Spawner()
        self.hud = HUD()
        self.screens = Screens()
        self.sprites = build_sprites()

        self.hazards: list = []
        self.cells: list = []
        self.elapsed = 0.0
        self.speed = config.BASE_SPEED
        self.score = 0.0
        self.cell_count = 0
        self.hi_score = load_hi_score()
        self.shake = 0.0
        self.flash = 0.0
        self.time = 0.0
        self.paused = False
        self.slide_held = False
        self.new_best = False

    # -- flow ------------------------------------------------------------------
    def reset_run(self) -> None:
        self.player.reset()
        self.particles.clear()
        self.hazards.clear()
        self.cells.clear()
        self.spawner.reset(seed=random.randint(0, 10_000_000))
        self.elapsed = 0.0
        self.speed = config.BASE_SPEED
        self.score = 0.0
        self.cell_count = 0
        self.shake = 0.0
        self.flash = 0.0
        self.paused = False
        self.slide_held = False
        self.new_best = False

    def start_run(self) -> None:
        self.reset_run()
        self.state = GameState.PLAYING
        self.sound.play_ui()

    def to_start(self) -> None:
        self.reset_run()
        self.state = GameState.START

    def game_over(self) -> None:
        self.state = GameState.GAME_OVER
        self.player.dead = True
        final = int(self.score)
        self.new_best = final > self.hi_score
        if self.new_best:
            self.hi_score = final
            save_hi_score(final)
        self.shake = config.SCREEN_SHAKE_MAGNITUDE
        self.flash = 0.55
        self.particles.crash(*self.player.center)
        self.sound.play_crash()

    # -- input -------------------------------------------------------------------
    def _is_jump_key(self, key: int) -> bool:
        return key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return False to quit the application."""
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            # NOTE: pygame KEYDOWN events carry no `repeat` attribute, so
            # getattr with a default keeps held-key repeats from double-firing
            # without raising AttributeError.
            is_repeat = bool(getattr(event, "repeat", 0))
            if self.state == GameState.START:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP):
                    self.start_run()
            elif self.state == GameState.PLAYING:
                if self._is_jump_key(event.key) and not is_repeat:
                    self.player.press_jump()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    self.sound.play_ui()
            elif self.state == GameState.GAME_OVER:
                if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    self.start_run()
                elif event.key == pygame.K_m:
                    self.to_start()
        elif event.type == pygame.KEYUP:
            if self.state == GameState.PLAYING and self._is_jump_key(event.key):
                self.player.release_jump()
        return True

    def _poll_held_keys(self) -> None:
        keys = pygame.key.get_pressed()
        self.slide_held = bool(keys[pygame.K_DOWN] or keys[pygame.K_s])
        # Also treat jump-held for variable height continuity (no-op if tapped).
        if not (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            # Key physically up but KEYUP may have been missed on state change.
            self.player.jump_held = False

    # -- update --------------------------------------------------------------------
    def update(self, dt: float) -> None:
        self.time += dt
        self.background.update(dt, self.speed if self.state == GameState.PLAYING and not self.paused else 0.0)
        # Decay shake / flash in every state so menus settle.
        self.shake = max(0.0, self.shake - config.SCREEN_SHAKE_DECAY * dt)
        self.flash = max(0.0, self.flash - dt * 1.8)
        self.particles.update(dt)

        if self.state != GameState.PLAYING or self.paused:
            # Idle menu animation: keep cells/hazards drifting slowly on START.
            if self.state == GameState.START:
                for c in self.cells:
                    c.update(dt, 60.0, self.time)
                self.cells = [c for c in self.cells if not c.offscreen]
            return

        self._poll_held_keys()
        self.elapsed += dt
        self.speed = min(config.MAX_SPEED, config.BASE_SPEED + self.elapsed * config.SPEED_RAMP)
        self.score += config.SCORE_PER_SECOND * dt * (self.speed / config.BASE_SPEED)

        self.player.update(dt, self.particles, slide_held=self.slide_held, sound=self.sound)
        self.spawner.update(dt, self.speed, self.elapsed, self)

        for h in self.hazards:
            h.update(dt, self.speed, self.time)
        for c in self.cells:
            c.update(dt, self.speed, self.time)
        self.hazards = [h for h in self.hazards if not h.offscreen]
        self.cells = [c for c in self.cells if not c.offscreen]

        # Pickups first (feel-good), then lethal checks.
        prect = self.player.rect
        for cell in list(self.cells):
            if prect.colliderect(cell.rect):
                cell.taken = True
                self.cells.remove(cell)
                self.cell_count += 1
                self.score += config.CELL_BONUS
                self.particles.pickup_sparkle(cell.x, cell.y)
                self.sound.play_pickup()

        for hazard in self.hazards:
            if collides(prect, hazard.rect):
                self.game_over()
                break

    # -- render ----------------------------------------------------------------------
    def _shake_offset(self) -> tuple[float, float]:
        if self.shake <= 0.0:
            return (0.0, 0.0)
        mag = self.shake
        return (
            random.uniform(-mag, mag) * (mag / config.SCREEN_SHAKE_MAGNITUDE),
            random.uniform(-mag, mag) * (mag / config.SCREEN_SHAKE_MAGNITUDE),
        )

    def render(self) -> None:
        ox, oy = self._shake_offset()
        self.background.draw(self.surface)
        # World-space drawing with shake applied via a translated subsurface?
        # Cheaper: pass offset into entity draws manually.
        # World-space entities share the screen-shake offset via draw params;
        # simulation state is never mutated for rendering.
        for cell in self.cells:
            cell.draw(self.surface, ox, oy)
        for hazard in self.hazards:
            hazard.draw(self.surface, ox, oy)

        if self.state != GameState.GAME_OVER:
            self.player.draw(self.surface, self.sprites, ox, oy)
        # Else (GAME_OVER): player stays hidden inside the crash explosion.
        self.particles.draw(self.surface, (ox, oy))

        # Track glow line on top of world.
        pygame.draw.line(self.surface, config.TRACK_LINE,
                         (0, config.GROUND_Y), (config.WIDTH, config.GROUND_Y), 2)

        self.hud.draw(
            self.surface,
            score=int(self.score),
            hi_score=self.hi_score,
            speed=self.speed,
            cells=self.cell_count,
            fps=self.clock.get_fps(),
            state=self.state,
            paused=self.paused,
        )
        if self.state == GameState.START:
            self.screens.draw_start(self.surface, self.time, self.hi_score)
        elif self.state == GameState.GAME_OVER:
            self.screens.draw_game_over(
                self.surface, self.time, int(self.score), self.hi_score,
                self.cell_count, self.new_best,
            )
        elif self.paused:
            self.screens.draw_paused(self.surface)

        if self.flash > 0.0:
            veil = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            veil.fill((255, 40, 120, int(120 * (self.flash / 0.55))))
            self.surface.blit(veil, (0, 0))

    # -- main loop ----------------------------------------------------------------------
    def run(self) -> None:
        running = True
        # Seed an ambient cell drift on the start screen.
        for i in range(4):
            self.cells.append(EnergyCell(300.0 + i * 140.0, config.GROUND_Y - 150.0))
        while running:
            dt = min(self.clock.tick(config.FPS) / 1000.0, config.MAX_DT)
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
                    break
            if not running:
                break
            self.update(dt)
            self.render()
            pygame.display.flip()
