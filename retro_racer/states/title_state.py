"""Title Screen State with Track Selector and Arcade Navigation."""

import math
from typing import List
import pygame

from retro_racer.engine.state_manager import State
from retro_racer.ui.menu import MenuButton
from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_CYAN, COLOR_YELLOW,
    COLOR_WHITE, COLOR_GOLD, COLOR_RED, COLOR_MAGENTA
)


class TitleState(State):
    """Arcade title screen menu and track selection."""

    def __init__(self, engine):
        super().__init__(engine)
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 28)
        self.font_sub = pygame.font.SysFont("Consolas, Courier New", 11, bold=True)
        self.font_track = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 15)

        self.buttons: List[MenuButton] = []
        self.selected_btn_idx = 0
        self.available_tracks = []
        self.selected_track_idx = 0

        self._init_menu()

    def _init_menu(self):
        btn_w, btn_h = 240, 36
        start_y = 230
        spacing = 46

        options = [
            ("START RACE", "play"),
            ("GARAGE & UPGRADES", "garage"),
            ("TRACK LEVEL EDITOR", "editor"),
            ("SAVED REPLAYS", "replay"),
            ("HALL OF FAME", "leaderboard"),
            ("SETTINGS", "settings"),
            ("EXIT", "exit"),
        ]

        self.buttons = [
            MenuButton(
                pygame.Rect((VIRTUAL_WIDTH - btn_w) // 2, start_y + i * spacing, btn_w, btn_h),
                text,
                action_id,
                font_size=15,
                primary_color=COLOR_CYAN if action_id != "play" else COLOR_YELLOW
            )
            for i, (text, action_id) in enumerate(options)
        ]

    def on_enter(self, **kwargs):
        self.engine.audio_mgr.start_music()
        self.available_tracks = self.engine.level_editor.list_tracks()
        if not self.available_tracks:
            self.engine.level_editor.generate_default_tracks()
            self.available_tracks = self.engine.level_editor.list_tracks()
        self.selected_track_idx = 0

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler

        # Keyboard Navigation
        if input_mgr.is_action_just_pressed("up"):
            self.selected_btn_idx = (self.selected_btn_idx - 1) % len(self.buttons)
            self.engine.audio_mgr.play_sfx("beep")
        elif input_mgr.is_action_just_pressed("down"):
            self.selected_btn_idx = (self.selected_btn_idx + 1) % len(self.buttons)
            self.engine.audio_mgr.play_sfx("beep")
        elif input_mgr.is_action_just_pressed("left"):
            if self.available_tracks:
                self.selected_track_idx = (self.selected_track_idx - 1) % len(self.available_tracks)
                self.engine.audio_mgr.play_sfx("beep")
        elif input_mgr.is_action_just_pressed("right"):
            if self.available_tracks:
                self.selected_track_idx = (self.selected_track_idx + 1) % len(self.available_tracks)
                self.engine.audio_mgr.play_sfx("beep")
        elif input_mgr.is_action_just_pressed("confirm"):
            self._trigger_action(self.buttons[self.selected_btn_idx].action_id)

        # Mouse Navigation
        for i, btn in enumerate(self.buttons):
            if btn.check_hover(input_mgr.mouse_pos):
                self.selected_btn_idx = i
                if input_mgr.mouse_just_pressed:
                    self._trigger_action(btn.action_id)

    def _trigger_action(self, action_id: str):
        self.engine.audio_mgr.play_sfx("beep")
        if action_id == "play":
            track = self.available_tracks[self.selected_track_idx] if self.available_tracks else None
            self.engine.state_mgr.change_state("play", track_data=track)
        elif action_id == "garage":
            self.engine.state_mgr.change_state("garage")
        elif action_id == "editor":
            self.engine.state_mgr.change_state("editor")
        elif action_id == "replay":
            self.engine.state_mgr.change_state("replay")
        elif action_id == "leaderboard":
            self.engine.state_mgr.change_state("leaderboard")
        elif action_id == "settings":
            self.engine.state_mgr.change_state("settings")
        elif action_id == "exit":
            self.engine.running = False

    def update(self, dt: float):
        for i, btn in enumerate(self.buttons):
            btn.is_selected = (i == self.selected_btn_idx)

    def render(self, surface: pygame.Surface):
        # Synthwave dark gradient backdrop
        surface.fill((14, 10, 24))

        # Animated retro grid lines
        t = pygame.time.get_ticks() * 0.001
        for y in range(0, VIRTUAL_HEIGHT, 24):
            pygame.draw.line(surface, (35, 20, 55), (0, y), (VIRTUAL_WIDTH, y), 1)

        # Glowing Title
        glow_pulse = math.sin(t * 4.0) * 4
        title_surf = self.font_title.render("RETRO RACER PYTHON", True, COLOR_YELLOW)
        glow_surf = self.font_title.render("RETRO RACER PYTHON", True, COLOR_MAGENTA)
        cx = VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2
        surface.blit(glow_surf, (cx + 2, 42))
        surface.blit(title_surf, (cx, 40))

        sub_surf = self.font_sub.render("16-BIT HIGH SPEED ARCADE ENGINE", True, COLOR_CYAN)
        surface.blit(sub_surf, (VIRTUAL_WIDTH // 2 - sub_surf.get_width() // 2, 80))

        # Track Selector Card
        if self.available_tracks:
            track = self.available_tracks[self.selected_track_idx]
            card_rect = pygame.Rect(40, 115, VIRTUAL_WIDTH - 80, 80)
            pygame.draw.rect(surface, (20, 24, 38), card_rect)
            pygame.draw.rect(surface, (0, 220, 255), card_rect, width=1)

            t_lbl = self.font_sub.render("<< SELECT TRACK [LEFT / RIGHT] >>", True, (160, 180, 210))
            surface.blit(t_lbl, (card_rect.centerx - t_lbl.get_width() // 2, card_rect.top + 8))

            name_s = self.font_track.render(track.name, True, COLOR_GOLD)
            surface.blit(name_s, (card_rect.centerx - name_s.get_width() // 2, card_rect.top + 28))

            diff_s = self.font_sub.render(f"Difficulty: {track.difficulty} | Biome: {track.biome.upper()}", True, COLOR_WHITE)
            surface.blit(diff_s, (card_rect.centerx - diff_s.get_width() // 2, card_rect.top + 54))

        # Menu Buttons
        for btn in self.buttons:
            btn.render(surface)

        # Footer controls hint
        footer = self.font_sub.render("[UP/DOWN] Select  [ENTER/SPACE] Confirm  [ESC] Back", True, (140, 150, 170))
        surface.blit(footer, (VIRTUAL_WIDTH // 2 - footer.get_width() // 2, VIRTUAL_HEIGHT - 24))
