"""In-game F3 Debug Tool and System Diagnostics."""

from typing import Dict, Any, List
import pygame

from retro_racer.config import COLOR_WHITE, COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_CYAN


class DebugOverlay:
    """Renders debug performance metrics, hitboxes, and state inspector."""

    def __init__(self):
        self.enabled = False
        self.show_hitboxes = False
        self.god_mode = False
        self.infinite_nitro = False
        self.font = None

    def _ensure_font(self):
        if self.font is None:
            pygame.font.init()
            self.font = pygame.font.SysFont("Consolas", 12, bold=True)

    def toggle(self):
        self.enabled = not self.enabled

    def toggle_hitboxes(self):
        self.show_hitboxes = not self.show_hitboxes

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
        bg_surf = pygame.Surface((220, 240), pygame.SRCALPHA)
        bg_surf.fill((10, 15, 25, 210))
        surface.blit(bg_surf, (8, 8))
        pygame.draw.rect(surface, (0, 230, 255), (8, 8, 220, 240), width=1)

        lines = [
            ("=== DEBUG MONITOR (F3) ===", COLOR_CYAN),
            (f"FPS: {stats.get('fps', 0):.1f} (dt: {stats.get('dt', 0)*1000:.1f}ms)", COLOR_GREEN),
            (f"Pos X: {stats.get('pos_x', 0):.1f} | Y: {stats.get('pos_y', 0):.1f}", COLOR_WHITE),
            (f"Speed: {stats.get('speed', 0):.1f} px/s ({stats.get('speed_kmh', 0):.0f} km/h)", COLOR_YELLOW),
            (f"Fuel: {stats.get('fuel', 0):.1f}% | Nitro: {stats.get('nitro', 0):.1f}%", COLOR_WHITE),
            (f"Health: {stats.get('health', 0):.0f}% | Score: {stats.get('score', 0)}", COLOR_WHITE),
            (f"Track: {stats.get('track_name', 'None')}", COLOR_CYAN),
            (f"Curvature: {stats.get('curvature', 0.0):.2f}", COLOR_WHITE),
            (f"Traffic count: {stats.get('traffic_count', 0)}", COLOR_WHITE),
            (f"Particles: {stats.get('particles', 0)}", COLOR_WHITE),
            ("--- CHEATS / TOGGLES ---", (180, 180, 200)),
            (f"[G] God Mode: {'ON' if self.god_mode else 'OFF'}", COLOR_GREEN if self.god_mode else COLOR_RED),
            (f"[N] Inf Nitro: {'ON' if self.infinite_nitro else 'OFF'}", COLOR_GREEN if self.infinite_nitro else COLOR_RED),
            (f"[H] Hitboxes: {'ON' if self.show_hitboxes else 'OFF'}", COLOR_GREEN if self.show_hitboxes else COLOR_RED),
            ("[T] Spawn Traffic | [U] Spawn Item", (160, 160, 170)),
        ]

        y = 12
        for text, col in lines:
            txt_surf = self.font.render(text, True, col)
            surface.blit(txt_surf, (14, y))
            y += 15

    def draw_hitbox(self, surface: pygame.Surface, rect: pygame.Rect, color=(0, 255, 0)):
        """Draw outline hitbox rectangle if hitboxes enabled."""
        if self.show_hitboxes or self.enabled:
            pygame.draw.rect(surface, color, rect, width=1)
