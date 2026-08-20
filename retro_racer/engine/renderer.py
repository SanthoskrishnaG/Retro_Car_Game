"""Post-processing, CRT Scanlines, Nearest-Neighbor Scaling, and Visual FX Renderer."""

import random
from typing import List, Tuple, Dict, Any
import pygame

from retro_racer.config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_CYAN, COLOR_YELLOW, COLOR_WHITE, COLOR_RED


class FloatingText:
    """Animated floating text popup for near-misses, combos, and score rewards."""

    def __init__(self, text: str, x: float, y: float, color: Tuple[int, int, int] = COLOR_YELLOW,
                 duration: float = 1.0, font_size: int = 12):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.age = 0.0
        self.font_size = font_size
        self.is_alive = True

    def update(self, dt: float):
        self.age += dt
        self.y -= 25.0 * dt
        if self.age >= self.duration:
            self.is_alive = False

    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        if not self.is_alive:
            return
        alpha = int(255 * (1.0 - (self.age / self.duration)))
        shadow_surf = font.render(self.text, True, (10, 10, 15))
        shadow_surf.set_alpha(alpha)
        surface.blit(shadow_surf, (int(self.x) + 1, int(self.y) + 1))

        txt_surf = font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        surface.blit(txt_surf, (int(self.x), int(self.y)))


class Renderer:
    """Handles virtual canvas scaling, aspect ratio preservation, nearest-neighbor scaling, and CRT scanlines."""

    def __init__(self, virtual_w: int = VIRTUAL_WIDTH, virtual_h: int = VIRTUAL_HEIGHT):
        self.virtual_w = virtual_w
        self.virtual_h = virtual_h
        self.virtual_surface = pygame.Surface((virtual_w, virtual_h))

        # CRT Scanlines toggle
        self.enable_crt = True
        self._scanline_surface = self._create_scanline_overlay()

        # Speed lines
        self.speed_lines: List[List[float]] = []
        self._init_speed_lines()

        # Floating texts
        self.floating_texts: List[FloatingText] = []
        pygame.font.init()
        self.font_small = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 10)
        self.font_med = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 12)
        self.font_large = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 16)

    def _create_scanline_overlay(self) -> pygame.Surface:
        """Create transparent CRT scanline texture."""
        surf = pygame.Surface((self.virtual_w, self.virtual_h), pygame.SRCALPHA)
        for y in range(0, self.virtual_h, 2):
            pygame.draw.line(surf, (0, 0, 0, 40), (0, y), (self.virtual_w, y))
        return surf

    def _init_speed_lines(self):
        self.speed_lines.clear()
        for _ in range(18):
            x = random.randint(10, self.virtual_w - 10)
            y = random.randint(0, self.virtual_h)
            length = random.randint(15, 45)
            speed = random.uniform(500, 900)
            self.speed_lines.append([float(x), float(y), float(length), speed])

    def add_floating_text(self, text: str, x: float, y: float, color=COLOR_YELLOW):
        self.floating_texts.append(FloatingText(text, x, y, color))

    def update(self, dt: float, is_high_speed: bool = False, speed_ratio: float = 0.0):
        """Update speed lines and floating text animations."""
        for line in self.speed_lines:
            mult = 1.6 if is_high_speed else (0.5 + speed_ratio)
            line[1] += line[3] * dt * mult
            if line[1] > self.virtual_h:
                line[1] = -line[2]
                line[0] = random.randint(15, self.virtual_w - 15)

        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.is_alive]

    def render_speed_lines(self, surface: pygame.Surface, is_nitro: bool = False):
        col = (200, 240, 255, 140) if is_nitro else (255, 255, 255, 70)
        for line in self.speed_lines:
            x, y, length, _ = line
            pygame.draw.line(surface, col, (int(x), int(y)), (int(x), int(y + length)), width=1)

    def render_floating_texts(self, surface: pygame.Surface):
        for ft in self.floating_texts:
            ft.render(surface, self.font_med)

    def render_to_screen(self, screen: pygame.Surface, is_nitro: bool = False):
        """Render virtual canvas to desktop window using nearest-neighbor scaling and aspect-ratio letterboxing."""
        if self.enable_crt:
            self.virtual_surface.blit(self._scanline_surface, (0, 0))

        sw, sh = screen.get_size()

        # Aspect ratio preservation
        scale_x = sw / self.virtual_w
        scale_y = sh / self.virtual_h
        scale = min(scale_x, scale_y)

        # For integer scaling when possible
        if scale >= 1.0:
            int_scale = int(scale)
            # Use nearest integer multiple if close, or exact float scale
            draw_w = int(self.virtual_w * scale)
            draw_h = int(self.virtual_h * scale)
        else:
            draw_w = int(self.virtual_w * scale)
            draw_h = int(self.virtual_h * scale)

        dest_x = (sw - draw_w) // 2
        dest_y = (sh - draw_h) // 2

        # Nearest-Neighbor scaling - preserves razor sharp retro pixels without blurring
        scaled = pygame.transform.scale(self.virtual_surface, (draw_w, draw_h))

        # Fill black letterbox / pillarbox margins
        screen.fill((0, 0, 0))
        screen.blit(scaled, (dest_x, dest_y))
