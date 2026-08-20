"""Garage and Vehicle Tuning UI with upgrade levels and car selection."""

import math
from typing import Dict, Any, List
import pygame

from retro_racer.config import (
    COLOR_WHITE, COLOR_GOLD, COLOR_CYAN, COLOR_YELLOW,
    COLOR_GREEN, COLOR_RED, VIRTUAL_WIDTH, VIRTUAL_HEIGHT
)


class GarageUI:
    """Renders car showroom, tuning stats, and upgrade purchasing cards."""

    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 14)
        self.font_med = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 11)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New", 9, bold=True)

        self.cars = [
            ("player_red", "Red Viper", 0),
            ("player_cyan", "Cyber Phantom", 0),
            ("player_yellow", "Solar Fury", 600),
            ("player_purple", "Neon Shadow", 900),
            ("player_black", "Midnight Stealth", 1400),
            ("player_green", "Emerald Apex", 2000),
        ]
        self.selected_car_idx = 0

        self.upgrade_defs = [
            ("top_speed", "Top Speed", 250),
            ("accel", "Acceleration", 200),
            ("handling", "Handling", 180),
            ("nitro", "Nitro Boost", 220),
            ("fuel_efficiency", "Fuel Eco", 150),
        ]

    def render(self, surface: pygame.Surface, career_profile: Dict[str, Any],
               asset_pipeline, is_unlocked: bool, selected_car_id: str):
        """Render complete Garage showroom interface."""
        surface.fill((12, 16, 26))

        # Title Header
        title_surf = self.font_title.render("GARAGE & PERFORMANCE TUNING", True, COLOR_GOLD)
        surface.blit(title_surf, (VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 6))

        # Credits Bar
        credits = career_profile.get("credits", 0)
        cr_surf = self.font_mono.render(f"WALLET: ${credits:,} CR", True, COLOR_GREEN)
        surface.blit(cr_surf, (VIRTUAL_WIDTH // 2 - cr_surf.get_width() // 2, 22))

        # 1. Car Showroom Platform
        self._render_car_podium(surface, asset_pipeline, is_unlocked)

        # 2. Upgrade Cards
        self._render_upgrade_list(surface, career_profile)

    def _render_car_podium(self, surface: pygame.Surface, asset_pipeline, is_unlocked: bool):
        podium_rect = pygame.Rect(14, 38, VIRTUAL_WIDTH - 28, 64)
        pygame.draw.rect(surface, (18, 24, 38), podium_rect)
        pygame.draw.rect(surface, (0, 220, 255), podium_rect, width=1)

        car_id, car_name, unlock_cost = self.cars[self.selected_car_idx]

        # Rotating neon glow ring under car
        cx, cy = podium_rect.centerx, podium_rect.centery - 6
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 3
        pygame.draw.ellipse(surface, (0, 180, 240, 100), (cx - 24 - pulse, cy + 12, 48 + pulse * 2, 12), width=1)

        # Draw vehicle sprite
        sprite = asset_pipeline.get_surface(car_id, pygame)
        if sprite:
            surface.blit(sprite, (cx - sprite.get_width() // 2, cy - sprite.get_height() // 2))

        # Car Name & Status
        name_surf = self.font_med.render(car_name, True, COLOR_WHITE)
        surface.blit(name_surf, (cx - name_surf.get_width() // 2, podium_rect.bottom - 18))

        if is_unlocked:
            stat_surf = self.font_mono.render("[OWNED]", True, COLOR_GREEN)
        else:
            stat_surf = self.font_mono.render(f"[${unlock_cost} CR]", True, COLOR_YELLOW)
        surface.blit(stat_surf, (podium_rect.right - stat_surf.get_width() - 8, podium_rect.bottom - 16))

    def _render_upgrade_list(self, surface: pygame.Surface, profile: Dict[str, Any]):
        start_y = 108
        card_h = 20
        credits = profile.get("credits", 0)

        for i, (up_key, up_name, base_cost) in enumerate(self.upgrade_defs):
            lvl_col = f"upgrade_{up_key}"
            curr_lvl = profile.get(lvl_col, 0)
            cost = base_cost * (curr_lvl + 1)
            is_max = curr_lvl >= 5

            card_rect = pygame.Rect(14, start_y + (i * (card_h + 3)), VIRTUAL_WIDTH - 28, card_h)
            pygame.draw.rect(surface, (20, 26, 40), card_rect)
            pygame.draw.rect(surface, (50, 60, 80), card_rect, width=1)

            # Name
            name_surf = self.font_med.render(up_name, True, COLOR_WHITE)
            surface.blit(name_surf, (card_rect.left + 6, card_rect.top + 3))

            # Level Pips
            pip_str = "LVL: " + ("■ " * curr_lvl) + ("□ " * (5 - curr_lvl))
            pip_surf = self.font_mono.render(pip_str, True, COLOR_CYAN if not is_max else COLOR_GOLD)
            surface.blit(pip_surf, (card_rect.left + 90, card_rect.top + 5))

            # Price
            if is_max:
                pr_surf = self.font_med.render("MAX", True, COLOR_GOLD)
            else:
                can_afford = credits >= cost
                pr_col = COLOR_GREEN if can_afford else COLOR_RED
                pr_surf = self.font_mono.render(f"${cost}", True, pr_col)
            surface.blit(pr_surf, (card_rect.right - pr_surf.get_width() - 56, card_rect.centery - pr_surf.get_height() // 2))
