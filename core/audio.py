"""Procedural retro synth SFX — zero audio files required.

Tones are synthesized into 16-bit PCM buffers with the stdlib ``array``
module, so there is no numpy dependency. If the mixer cannot be opened
(headless CI, missing device), a silent stub keeps the game running.
"""

from __future__ import annotations

import array
import math

import config


def _tone(
    freq: float,
    duration: float,
    volume: float = 0.5,
    slide_to: float | None = None,
    wave: str = "square",
) -> array.array:
    rate = config.AUDIO_FREQUENCY
    n = max(1, int(rate * duration))
    buf = array.array("h")
    phase = 0.0
    for i in range(n):
        t = i / n
        f = freq if slide_to is None else freq + (slide_to - freq) * t
        phase += 2.0 * math.pi * f / rate
        if wave == "square":
            s = 1.0 if math.sin(phase) >= 0.0 else -1.0
        elif wave == "saw":
            s = 2.0 * ((phase / (2.0 * math.pi)) % 1.0) - 1.0
        elif wave == "noise":
            # Deterministic pseudo-noise so SFX are stable run to run.
            s = ((1103515245 * (i + 1) + 12345) >> 16) / 32768.0
        else:  # sine
            s = math.sin(phase)
        env = 1.0 - t  # linear decay avoids clicks
        env = env * env
        buf.append(int(max(-1.0, min(1.0, s * volume * env)) * 32767))
    return buf


class _SilentSound:
    def play(self, *args, **kwargs):  # noqa: ANN002, ANN003, D102
        return None

    def set_volume(self, *args, **kwargs):  # noqa: ANN002, ANN003, D102
        return None


class SoundBank:
    """Owns all synthesized effects; safe to use when audio is unavailable."""

    def __init__(self) -> None:
        self.enabled = False
        self.jump = _SilentSound()
        self.slide = _SilentSound()
        self.pickup = _SilentSound()
        self.crash = _SilentSound()
        self.ui = _SilentSound()
        if not config.AUDIO_ENABLED:
            return
        try:
            import pygame

            pygame.mixer.pre_init(config.AUDIO_FREQUENCY, -16, 1, config.AUDIO_BUFFER)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)
            self.jump = pygame.mixer.Sound(buffer=_tone(320, 0.16, 0.35, slide_to=720))
            self.slide = pygame.mixer.Sound(buffer=_tone(220, 0.12, 0.25, slide_to=110, wave="saw"))
            self.pickup = pygame.mixer.Sound(buffer=_tone(880, 0.14, 0.35, slide_to=1560, wave="sine"))
            self.crash = pygame.mixer.Sound(buffer=_tone(160, 0.45, 0.5, slide_to=40, wave="noise"))
            self.ui = pygame.mixer.Sound(buffer=_tone(660, 0.07, 0.3, wave="sine"))
            for s in (self.jump, self.slide, self.pickup, self.crash, self.ui):
                try:
                    s.set_volume(config.MASTER_VOLUME)
                except Exception:
                    pass
            self.enabled = True
        except Exception:
            # Headless / no audio device: stay silent, game still runs.
            self.enabled = False

    # -- convenience wrappers -------------------------------------------
    def play_jump(self) -> None:
        self.jump.play()

    def play_slide(self) -> None:
        self.slide.play()

    def play_pickup(self) -> None:
        self.pickup.play()

    def play_crash(self) -> None:
        self.crash.play()

    def play_ui(self) -> None:
        self.ui.play()
