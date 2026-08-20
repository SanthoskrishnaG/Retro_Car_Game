"""In-game Developer Diagnostics: F3 Collision Boxes & F4 Object Boundaries."""

from typing import Dict, Any, List
import pygame

from retro_racer.config import COLOR_WHITE, COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_CYAN


class DebugOverlay:
    """Renders debug performance metrics, hitboxes (F3), and object boundaries / raycasts (F4)."""

    def __init__(self):
        self.enabled = False
        self.show_hitboxes = False      # F3 toggle
        self.show_boundaries = False    # F4 toggle
        self.god_mode = False
        self.infinite_nitro = False
        self.font = None

    def _ensure_font(self):
        if self.font is None:
            pygame.font.init()
            self.font = pygame.font.SysFont("Consolas, Courier New", 8, bold=True)

    def toggle(self):
        self.enabled = not self.enabled
        self.show_hitboxes = self.enabled

    def toggle_hitboxes(self):
        self.show_hitboxes = not self.show_hitboxes

    def toggle_boundaries(self):
        self.show_boundaries = not self.show_boundaries

    def toggle_god_mode(self):
        self.god_mode = not self.god_mode

    def toggle_infinite_nitro(self):
        self.infinite_nitro = not self.infinite_nitro

    def render(self, surface: pygame.Surface, stats: Dict[str, Any]):
        """Render debug readout overlay."""
        if not self.enabled:
            return

        self._ensure_font()

        # Debug semi-transparent background card
        bg_surf = pygame.Surface((155, 175), pygame.SRCALPHA)
        bg_surf.fill((10, 15, 25, 215))
        surface.blit(bg_surf, (4, 4))
        pygame.draw.rect(surface, (0, 230, 255), (4, 4, 155, 175), width=1)

        lines = [
            ("=== DEBUG (F3/F4) ===", COLOR_CYAN),
            (f"FPS: {stats.get('fps', 0):.1f} ({stats.get('dt', 0)*1000:.1f}ms)", COLOR_GREEN),
            (f"Pos X: {stats.get('pos_x', 0):.1f} | Y: {stats.get('pos_y', 0):.0f}", COLOR_WHITE),
            (f"Vel X: {stats.get('vel_x', 0):.1f} | Y: {stats.get('vel_y', 0):.0f}", COLOR_WHITE),
            (f"Speed: {stats.get('speed', 0):.0f}px ({stats.get('speed_kmh', 0):.0f}km/h)", COLOR_YELLOW),
            (f"Fuel: {stats.get('fuel', 0):.0f}% | N2O: {stats.get('nitro', 0):.0f}%", COLOR_WHITE),
            (f"HP: {stats.get('health', 0):.0f}% | Score: {stats.get('score', 0)}", COLOR_WHITE),
            (f"Traffic: {stats.get('traffic_count', 0)} | Props: {stats.get('scenery_count', 0)}", COLOR_WHITE),
            (f"Curvature: {stats.get('curvature', 0.0):.2f}", COLOR_CYAN),
            ("--- CHEATS ---", (160, 160, 180)),
            (f"[G] God Mode: {'ON' if self.god_mode else 'OFF'}", COLOR_GREEN if self.god_mode else COLOR_RED),
            (f"[N] Inf Nitro: {'ON' if self.infinite_nitro else 'OFF'}", COLOR_GREEN if self.infinite_nitro else COLOR_RED),
            (f"[F3] Hitboxes: {'ON' if self.show_hitboxes else 'OFF'}", COLOR_GREEN if self.show_hitboxes else COLOR_RED),
            (f"[F4] Bounds: {'ON' if self.show_boundaries else 'OFF'}", COLOR_GREEN if self.show_boundaries else COLOR_RED),
        ]

        y = 7
        for text, col in lines:
            txt_surf = self.font.render(text, True, col)
            surface.blit(txt_surf, (8, y))
            y += 11

    def draw_hitbox(self, surface: pygame.Surface, rect: pygame.Rect, color=(0, 255, 0)):
        """Draw outline hitbox rectangle."""
        if self.show_hitboxes or self.enabled:
            pygame.draw.rect(surface, color, rect, width=1)

    def draw_boundary(self, surface: pygame.Surface, rect: pygame.Rect, color=(255, 255, 0)):
        """Draw full sprite boundary box."""
        if self.show_boundaries or self.enabled:
            pygame.draw.rect(surface, color, rect, width=1)
