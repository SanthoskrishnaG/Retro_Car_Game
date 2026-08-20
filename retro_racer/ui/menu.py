"""Menu UI Elements: Glowing arcade buttons, panels, and leaderboard tables."""

from typing import List, Tuple, Callable, Optional
import pygame

from retro_racer.config import (
    COLOR_WHITE, COLOR_CYAN, COLOR_YELLOW, COLOR_RED,
    COLOR_GOLD, COLOR_DARK_GRAY, VIRTUAL_WIDTH, VIRTUAL_HEIGHT
)


class MenuButton:
    """Arcade-style glowing interactive button."""

    def __init__(self, rect: pygame.Rect, text: str, action_id: str,
                 font_size: int = 16, primary_color: Tuple[int, int, int] = COLOR_CYAN):
        self.rect = rect
        self.text = text
        self.action_id = action_id
        self.primary_color = primary_color
        self.is_hovered = False
        self.is_selected = False

        pygame.font.init()
        self.font = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", font_size)

    def check_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def render(self, surface: pygame.Surface):
        active = self.is_hovered or self.is_selected

        # Button background
        bg_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if active:
            bg_surf.fill((*self.primary_color[:3], 140))
        else:
            bg_surf.fill((15, 20, 30, 200))
        surface.blit(bg_surf, self.rect.topleft)

        # Border
        border_col = (255, 255, 255) if active else self.primary_color
        pygame.draw.rect(surface, border_col, self.rect, width=2 if active else 1)

        # Text
        txt_col = COLOR_WHITE if active else (210, 220, 240)
        txt_surf = self.font.render(self.text, True, txt_col)
        tx = self.rect.centerx - txt_surf.get_width() // 2
        ty = self.rect.centery - txt_surf.get_height() // 2
        surface.blit(txt_surf, (tx, ty))


class MenuPanel:
    """Semi-transparent retro modal window container."""

    def __init__(self, rect: pygame.Rect, title: str = "", border_color: Tuple[int, int, int] = COLOR_CYAN):
        self.rect = rect
        self.title = title
        self.border_color = border_color
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 20)

    def render(self, surface: pygame.Surface):
        # Panel body
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        surf.fill((10, 14, 22, 235))
        surface.blit(surf, self.rect.topleft)
        pygame.draw.rect(surface, self.border_color, self.rect, width=2)

        # Title banner
        if self.title:
            t_surf = self.font_title.render(self.title, True, COLOR_GOLD)
            surface.blit(t_surf, (self.rect.centerx - t_surf.get_width() // 2, self.rect.top + 12))
            pygame.draw.line(surface, self.border_color,
                             (self.rect.left + 16, self.rect.top + 40),
                             (self.rect.right - 16, self.rect.top + 40), 1)
