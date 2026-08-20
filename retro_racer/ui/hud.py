"""Retro Arcade Heads-Up Display (HUD) with gauges, speedometers, and status counters."""

import math
from typing import Dict, Any, Optional
import pygame

from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_WHITE, COLOR_YELLOW, COLOR_CYAN,
    COLOR_RED, COLOR_GREEN, COLOR_GOLD, NITRO_MAX, FUEL_MAX
)
from retro_racer.entities.player import PlayerCar


class HUD:
    """Renders gauges, speed dial, score, combo popups, and active buffs on retro canvas."""

    def __init__(self):
        pygame.font.init()
        self.font_large = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 14)
        self.font_mid = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 11)
        self.font_tiny = pygame.font.SysFont("Consolas, Courier New", 9, bold=True)

    def render(self, surface: pygame.Surface, player: PlayerCar, track_name: str, track_length: float, asset_pipeline):
        """Render complete in-game HUD interface."""
        # 1. Top Bar: Score & Distance
        self._render_top_bar(surface, player)

        # 2. Left Side: Fuel Gauge
        self._render_fuel_gauge(surface, player.fuel)

        # 3. Right Side: Nitro Boost Gauge
        self._render_nitro_gauge(surface, player.nitro, player.is_nitro_active)

        # 4. Bottom Right: Arcade Speedometer
        self._render_speedometer(surface, player.speed)

        # 5. Top Right: Power-Up Badges
        self._render_powerup_badges(surface, player, asset_pipeline)

        # 6. Bottom Center: Track Distance Progress Bar
        self._render_progress_bar(surface, player.y, track_length)

    def _render_top_bar(self, surface: pygame.Surface, player: PlayerCar):
        # Header banner
        header_surf = pygame.Surface((VIRTUAL_WIDTH, 26), pygame.SRCALPHA)
        header_surf.fill((10, 12, 20, 210))
        surface.blit(header_surf, (0, 0))
        pygame.draw.line(surface, (0, 220, 255), (0, 26), (VIRTUAL_WIDTH, 26), 1)

        # Score
        score_lbl = self.font_tiny.render("SCORE", True, (160, 170, 190))
        score_val = self.font_large.render(f"{player.score:07d}", True, COLOR_GOLD)
        surface.blit(score_lbl, (8, 2))
        surface.blit(score_val, (8, 10))

        # Multiplier indicator
        if player.double_score_timer > 0:
            mult_txt = self.font_tiny.render("2X BONUS!", True, COLOR_YELLOW)
            surface.blit(mult_txt, (80, 11))

        # Distance
        dist_lbl = self.font_tiny.render("DIST", True, (160, 170, 190))
        dist_val = self.font_large.render(f"{player.distance:.0f}M", True, COLOR_WHITE)
        surface.blit(dist_lbl, (VIRTUAL_WIDTH - 65, 2))
        surface.blit(dist_val, (VIRTUAL_WIDTH - 65, 10))

        # Combo display (if combo active)
        if player.combo_count > 1 and player.combo_timer > 0:
            combo_surf = self.font_mid.render(f"COMBO x{player.combo_count}", True, COLOR_CYAN)
            surface.blit(combo_surf, (VIRTUAL_WIDTH // 2 - combo_surf.get_width() // 2, 8))

    def _render_fuel_gauge(self, surface: pygame.Surface, fuel: float):
        # Fuel vertical meter on left edge
        gx, gy, gw, gh = 6, 32, 10, 65
        pygame.draw.rect(surface, (20, 25, 35), (gx, gy, gw, gh))
        pygame.draw.rect(surface, (70, 80, 100), (gx, gy, gw, gh), width=1)

        # Fuel fill
        pct = max(0.0, min(1.0, fuel / FUEL_MAX))
        fill_h = int(gh * pct)
        fill_y = gy + (gh - fill_h)

        col = COLOR_GREEN if pct > 0.35 else (COLOR_YELLOW if pct > 0.18 else COLOR_RED)
        if fill_h > 0:
            pygame.draw.rect(surface, col, (gx + 1, fill_y + 1, gw - 2, fill_h - 2))

        # 'F' / 'E' labels
        f_lbl = self.font_tiny.render("F", True, COLOR_WHITE)
        surface.blit(f_lbl, (gx + 2, gy + 2))
        e_lbl = self.font_tiny.render("E", True, COLOR_RED)
        surface.blit(e_lbl, (gx + 2, gy + gh - 10))

        lbl = self.font_tiny.render("GAS", True, (180, 190, 210))
        surface.blit(lbl, (gx - 2, gy + gh + 2))

    def _render_nitro_gauge(self, surface: pygame.Surface, nitro: float, is_active: bool):
        # Nitro vertical meter on right edge
        gx, gy, gw, gh = VIRTUAL_WIDTH - 16, 32, 10, 65
        pygame.draw.rect(surface, (20, 25, 35), (gx, gy, gw, gh))
        border_col = (0, 240, 255) if is_active else (70, 80, 100)
        pygame.draw.rect(surface, border_col, (gx, gy, gw, gh), width=1)

        pct = max(0.0, min(1.0, nitro / NITRO_MAX))
        fill_h = int(gh * pct)
        fill_y = gy + (gh - fill_h)

        nitro_col = (0, 230, 255) if not is_active else (255, 255, 255)
        if fill_h > 0:
            pygame.draw.rect(surface, nitro_col, (gx + 1, fill_y + 1, gw - 2, fill_h - 2))

        n_lbl = self.font_tiny.render("N2O", True, (0, 230, 255))
        surface.blit(n_lbl, (gx - 3, gy + gh + 2))

    def _render_speedometer(self, surface: pygame.Surface, speed: float):
        speed_kmh = int((speed / 380.0) * 220.0)
        panel_w, panel_h = 68, 30
        px = VIRTUAL_WIDTH - panel_w - 6
        py = VIRTUAL_HEIGHT - panel_h - 6

        card = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        card.fill((10, 15, 25, 220))
        surface.blit(card, (px, py))
        pygame.draw.rect(surface, (0, 220, 255), (px, py, panel_w, panel_h), width=1)

        val_surf = self.font_large.render(f"{speed_kmh:03d}", True, COLOR_CYAN)
        unit_surf = self.font_tiny.render("KM/H", True, (160, 180, 210))
        surface.blit(val_surf, (px + 6, py + 4))
        surface.blit(unit_surf, (px + panel_w - 26, py + 16))

    def _render_powerup_badges(self, surface: pygame.Surface, player: PlayerCar, asset_pipeline):
        bx = VIRTUAL_WIDTH - 24
        by = 30

        active_buffs = []
        if player.shield_timer > 0:
            active_buffs.append(("pickup_shield", player.shield_timer, COLOR_CYAN))
        if player.magnet_timer > 0:
            active_buffs.append(("pickup_magnet", player.magnet_timer, COLOR_YELLOW))
        if player.slowmo_timer > 0:
            active_buffs.append(("pickup_slowmo", player.slowmo_timer, COLOR_CYAN))
        if player.double_score_timer > 0:
            active_buffs.append(("pickup_2x", player.double_score_timer, COLOR_GOLD))

        for spr, timer, col in active_buffs:
            sprite = asset_pipeline.get_surface(spr, pygame)
            if sprite:
                # scale to 16x16
                scaled = pygame.transform.scale(sprite, (16, 16))
                surface.blit(scaled, (bx, by))
                t_surf = self.font_tiny.render(f"{timer:.0f}s", True, col)
                surface.blit(t_surf, (bx - 20, by + 2))
            by += 20

    def _render_progress_bar(self, surface: pygame.Surface, current_y: float, track_length: float):
        pw, ph = 100, 4
        px = (VIRTUAL_WIDTH - pw) // 2
        py = VIRTUAL_HEIGHT - 10

        pygame.draw.rect(surface, (25, 30, 40), (px, py, pw, ph))
        pygame.draw.rect(surface, (70, 80, 100), (px, py, pw, ph), width=1)

        progress = max(0.0, min(1.0, (current_y % track_length) / track_length))
        fill_w = int(pw * progress)
        if fill_w > 0:
            pygame.draw.rect(surface, (0, 220, 255), (px, py, fill_w, ph))

        pygame.draw.circle(surface, COLOR_YELLOW, (px + fill_w, py + ph // 2), 3)
