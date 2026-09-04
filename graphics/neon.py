"""Neon glow drawing primitives (all procedural, no assets)."""

from __future__ import annotations

import pygame


def _layered(surface: pygame.Surface, draw_fn, layers: int = 3, base_alpha: int = 90) -> None:
    for i in range(layers, 0, -1):
        draw_fn(i, base_alpha // i if i else base_alpha)


def glow_rect(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int], alpha: int = 90) -> None:
    """Soft outer glow behind a rect."""
    for i in (3, 2, 1):
        pad = i * 5
        ghost = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2), pygame.SRCALPHA)
        pygame.draw.rect(ghost, (*color, alpha // (i + 1)),
                         ghost.get_rect(), border_radius=6)
        surface.blit(ghost, (rect.x - pad, rect.y - pad))


def glow_circle(surface: pygame.Surface, pos: tuple[float, float], radius: int,
                color: tuple[int, int, int], alpha: int = 90) -> None:
    for i in (3, 2, 1):
        r = radius + i * 5
        ghost = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(ghost, (*color, alpha // (i + 1)), (r, r), r)
        surface.blit(ghost, (pos[0] - r, pos[1] - r))


def glow_polygon(surface: pygame.Surface, points: list[tuple[float, float]],
                 color: tuple[int, int, int], alpha: int = 80) -> None:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    pad = 12
    minx, miny = min(xs) - pad, min(ys) - pad
    shifted = [(x - minx, y - miny) for x, y in points]
    w = int(max(xs) - min(xs) + pad * 2)
    h = int(max(ys) - min(ys) + pad * 2)
    ghost = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
    pygame.draw.polygon(ghost, (*color, alpha), shifted)
    surface.blit(ghost, (minx, miny))


def h_line(surface: pygame.Surface, x1: float, x2: float, y: float,
           color: tuple[int, int, int], width: int = 2, alpha: int = 255) -> None:
    if alpha >= 255:
        pygame.draw.line(surface, color, (x1, y), (x2, y), width)
        return
    length = max(1, int(abs(x2 - x1)))
    ghost = pygame.Surface((length + 4, width + 4), pygame.SRCALPHA)
    pygame.draw.line(ghost, (*color, alpha), (2, 2 + width // 2), (2 + length, 2 + width // 2), width)
    surface.blit(ghost, (min(x1, x2) - 2, y - 2 - width // 2))


def v_line(surface: pygame.Surface, x: float, y1: float, y2: float,
           color: tuple[int, int, int], width: int = 2, alpha: int = 255) -> None:
    if alpha >= 255:
        pygame.draw.line(surface, color, (x, y1), (x, y2), width)
        return
    height = max(1, int(abs(y2 - y1)))
    ghost = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
    pygame.draw.line(ghost, (*color, alpha), (2 + width // 2, 2), (2 + width // 2, 2 + height), width)
    surface.blit(ghost, (x - 2 - width // 2, min(y1, y2) - 2))


def text_glow(surface: pygame.Surface, font: pygame.font.Font, text: str,
              pos: tuple[float, float], color: tuple[int, int, int],
              glow_color: tuple[int, int, int] | None = None, center: bool = False) -> None:
    glow_color = glow_color or color
    for offset, alpha in (((-2, 0), 60), ((2, 0), 60), ((0, -2), 60), ((0, 2), 60)):
        ghost = font.render(text, True, glow_color)
        ghost.set_alpha(alpha)
        r = ghost.get_rect()
        if center:
            r.center = (int(pos[0] + offset[0]), int(pos[1] + offset[1]))
        else:
            r.topleft = (int(pos[0] + offset[0]), int(pos[1] + offset[1]))
        surface.blit(ghost, r)
    main = font.render(text, True, color)
    r = main.get_rect()
    if center:
        r.center = (int(pos[0]), int(pos[1]))
    else:
        r.topleft = (int(pos[0]), int(pos[1]))
    surface.blit(main, r)
