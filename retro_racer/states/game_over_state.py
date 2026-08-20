"""Post-Race Game Over State with score breakdown and career earnings."""

from pathlib import Path
from typing import Optional
import pygame

from retro_racer.engine.state_manager import State
from retro_racer.ui.menu import MenuButton
from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_GOLD, COLOR_CYAN,
    COLOR_YELLOW, COLOR_WHITE, COLOR_GREEN, COLOR_RED
)


class GameOverState(State):
    """End-of-race tally screen saving score to SQLite and awarding career credits."""

    def __init__(self, engine):
        super().__init__(engine)
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 18)
        self.font_med = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 12)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New", 9, bold=True)

        self.score = 0
        self.distance = 0.0
        self.track_name = ""
        self.car_model = ""
        self.credits_earned = 0
        self.replay_path: Optional[Path] = None

        self.buttons = []
        self._init_buttons()

    def _init_buttons(self):
        cx = VIRTUAL_WIDTH // 2
        self.btn_retry = MenuButton(pygame.Rect(cx - 65, 162, 130, 20), "RACE AGAIN", "retry", font_size=10, primary_color=COLOR_GREEN)
        self.btn_garage = MenuButton(pygame.Rect(cx - 65, 186, 130, 20), "GARAGE & TUNING", "garage", font_size=10, primary_color=COLOR_CYAN)
        self.btn_menu = MenuButton(pygame.Rect(cx - 65, 210, 130, 20), "MAIN MENU", "menu", font_size=10, primary_color=COLOR_RED)

    def on_enter(self, score: int = 0, distance: float = 0.0, track_name: str = "City Track",
                 car_model: str = "player_red", replay_path: Optional[Path] = None, **kwargs):
        self.score = score
        self.distance = distance
        self.track_name = track_name
        self.car_model = car_model
        self.replay_path = replay_path

        # Credits earned
        self.credits_earned = int(score / 8.0) + int(distance / 5.0)

        # 1. Update Career Profile in SQLite
        self.engine.db.update_career_stats(self.credits_earned, self.distance)

        # 2. Add High Score to Leaderboard
        profile = self.engine.db.get_career_profile()
        player_name = profile.get("player_name", "Racer 1")
        self.engine.db.add_high_score(player_name, score, distance, track_name, car_model)

        # Sound
        self.engine.audio_mgr.play_sfx("coin")

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler
        if input_mgr.is_action_just_pressed("back") or input_mgr.is_action_just_pressed("pause"):
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")
            return

        all_buttons = [self.btn_retry, self.btn_garage, self.btn_menu]
        for btn in all_buttons:
            btn.check_hover(input_mgr.mouse_pos)
            if btn.is_hovered and input_mgr.mouse_just_pressed:
                self._handle_action(btn.action_id)

    def _handle_action(self, action_id: str):
        self.engine.audio_mgr.play_sfx("beep")
        if action_id == "retry":
            self.engine.state_mgr.change_state("play")
        elif action_id == "garage":
            self.engine.state_mgr.change_state("garage")
        elif action_id == "menu":
            self.engine.state_mgr.change_state("title")

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.fill((12, 14, 22))

        # Title
        t_s = self.font_title.render("RACE FINISHED", True, COLOR_GOLD)
        surface.blit(t_s, (VIRTUAL_WIDTH // 2 - t_s.get_width() // 2, 12))

        # Results Summary Card
        card_rect = pygame.Rect(20, 36, VIRTUAL_WIDTH - 40, 116)
        pygame.draw.rect(surface, (18, 22, 34), card_rect)
        pygame.draw.rect(surface, (0, 220, 255), card_rect, width=1)

        # Lines
        items = [
            ("Track:", self.track_name[:18], COLOR_WHITE),
            ("Final Score:", f"{self.score:,} PTS", COLOR_GOLD),
            ("Distance:", f"{self.distance:.0f} METERS", COLOR_CYAN),
            ("Earnings:", f"+${self.credits_earned:,} CR", COLOR_GREEN),
        ]

        y = card_rect.top + 10
        for label, val, col in items:
            lbl_s = self.font_med.render(label, True, (170, 180, 200))
            val_s = self.font_med.render(val, True, col)
            surface.blit(lbl_s, (card_rect.left + 12, y))
            surface.blit(val_s, (card_rect.right - val_s.get_width() - 12, y))
            y += 20

        # Saved badge
        saved_s = self.font_mono.render("[HIGH SCORE RECORDED]", True, COLOR_YELLOW)
        surface.blit(saved_s, (card_rect.centerx - saved_s.get_width() // 2, card_rect.bottom - 16))

        # Buttons
        self.btn_retry.render(surface)
        self.btn_garage.render(surface)
        self.btn_menu.render(surface)
