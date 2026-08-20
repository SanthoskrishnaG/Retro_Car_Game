"""Hall of Fame / Leaderboard State showing SQLite high scores."""

from typing import List, Dict, Any
import pygame

from retro_racer.engine.state_manager import State
from retro_racer.ui.menu import MenuButton
from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_GOLD, COLOR_CYAN,
    COLOR_YELLOW, COLOR_WHITE, COLOR_RED
)


class LeaderboardState(State):
    """Displays top scores stored in SQLite database."""

    def __init__(self, engine):
        super().__init__(engine)
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 14)
        self.font_head = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 10)
        self.font_row = pygame.font.SysFont("Consolas, Courier New", 8, bold=True)

        self.scores: List[Dict[str, Any]] = []
        self.btn_back = MenuButton(pygame.Rect(VIRTUAL_WIDTH // 2 - 50, VIRTUAL_HEIGHT - 20, 100, 16), "BACK TO MENU", "back", font_size=9, primary_color=COLOR_RED)

    def on_enter(self, **kwargs):
        self.scores = self.engine.db.get_top_scores(limit=7)

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler
        if input_mgr.is_action_just_pressed("back") or input_mgr.is_action_just_pressed("pause"):
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")
            return

        self.btn_back.check_hover(input_mgr.mouse_pos)
        if self.btn_back.is_hovered and input_mgr.mouse_just_pressed:
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.fill((12, 14, 22))

        # Title
        t_surf = self.font_title.render("HALL OF FAME — TOP DRIVERS", True, COLOR_GOLD)
        surface.blit(t_surf, (VIRTUAL_WIDTH // 2 - t_surf.get_width() // 2, 8))

        # Table Card
        card_rect = pygame.Rect(14, 28, VIRTUAL_WIDTH - 28, VIRTUAL_HEIGHT - 54)
        pygame.draw.rect(surface, (18, 22, 34), card_rect)
        pygame.draw.rect(surface, (0, 220, 255), card_rect, width=1)

        y = 34
        h_pos = self.font_head.render("POS", True, COLOR_CYAN)
        h_driver = self.font_head.render("DRIVER", True, COLOR_CYAN)
        h_dist = self.font_head.render("DIST", True, COLOR_CYAN)
        h_score = self.font_head.render("SCORE", True, COLOR_CYAN)

        surface.blit(h_pos, (22, y))
        surface.blit(h_driver, (55, y))
        surface.blit(h_dist, (160, y))
        surface.blit(h_score, (VIRTUAL_WIDTH - 70, y))

        pygame.draw.line(surface, (50, 60, 80), (20, y + 14), (VIRTUAL_WIDTH - 20, y + 14), 1)

        # Rows
        row_y = y + 18
        if not self.scores:
            no_scores = self.font_row.render("NO RECORDED HIGH SCORES YET", True, (140, 150, 170))
            surface.blit(no_scores, (VIRTUAL_WIDTH // 2 - no_scores.get_width() // 2, row_y + 30))
        else:
            for i, row in enumerate(self.scores):
                col = COLOR_GOLD if i == 0 else (COLOR_WHITE if i < 3 else (180, 190, 210))
                p_s = self.font_row.render(f"#{i+1}", True, col)
                d_s = self.font_row.render(str(row["player_name"])[:12], True, col)
                dist_s = self.font_row.render(f"{row['distance']:.0f}m", True, (160, 220, 255))
                sc_s = self.font_row.render(f"{row['score']:,}", True, COLOR_YELLOW)

                surface.blit(p_s, (22, row_y))
                surface.blit(d_s, (55, row_y))
                surface.blit(dist_s, (160, row_y))
                surface.blit(sc_s, (VIRTUAL_WIDTH - 70, row_y))

                row_y += 18

        self.btn_back.render(surface)
