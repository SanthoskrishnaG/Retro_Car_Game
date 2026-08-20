"""Replay Player State with timeline scrubbing and playback speed controls."""

from pathlib import Path
from typing import List
import pygame

from retro_racer.engine.state_manager import State
from retro_racer.engine.camera import Camera
from retro_racer.world.road import RoadSystem
from retro_racer.world.environment import get_environment_theme
from retro_racer.ui.menu import MenuButton
from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_CYAN, COLOR_YELLOW,
    COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED, ROAD_CENTER_X
)


class ReplayState(State):
    """Replay player with timeline scrubber and speed controls for 320x240 retro resolution."""

    def __init__(self, engine):
        super().__init__(engine)
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 14)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New", 8, bold=True)

        self.camera = Camera()
        self.road_system = RoadSystem()
        self.theme = get_environment_theme("synthwave")

        self.saved_files: List[Path] = []
        self.selected_file_idx = 0
        self.is_playing = False
        self.playback_speed = 1.0

        self.buttons = []
        self._init_buttons()

    def _init_buttons(self):
        cx = VIRTUAL_WIDTH // 2
        # File selector
        self.btn_prev_file = MenuButton(pygame.Rect(14, 24, 18, 16), "<", "prev_file", font_size=10)
        self.btn_next_file = MenuButton(pygame.Rect(VIRTUAL_WIDTH - 32, 24, 18, 16), ">", "next_file", font_size=10)

        # Player controls at bottom
        self.btn_play_pause = MenuButton(pygame.Rect(cx - 75, VIRTUAL_HEIGHT - 38, 38, 16), "PLAY", "toggle_play", font_size=8)
        self.btn_speed_slow = MenuButton(pygame.Rect(cx - 32, VIRTUAL_HEIGHT - 38, 28, 16), "0.5X", "speed_0.5", font_size=8)
        self.btn_speed_norm = MenuButton(pygame.Rect(cx, VIRTUAL_HEIGHT - 38, 28, 16), "1.0X", "speed_1.0", font_size=8)
        self.btn_speed_fast = MenuButton(pygame.Rect(cx + 32, VIRTUAL_HEIGHT - 38, 28, 16), "2.0X", "speed_2.0", font_size=8)

        self.btn_back = MenuButton(pygame.Rect(cx - 50, VIRTUAL_HEIGHT - 18, 100, 15), "BACK TO MENU", "back", font_size=8, primary_color=COLOR_RED)

    def on_enter(self, **kwargs):
        self.saved_files = self.engine.replay_mgr.list_saved_replays()
        self.selected_file_idx = 0
        self.is_playing = False
        if self.saved_files:
            self._load_selected_file()

    def _load_selected_file(self):
        if not self.saved_files:
            return
        filepath = self.saved_files[self.selected_file_idx]
        if self.engine.replay_mgr.load_replay(filepath):
            self.is_playing = True

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler
        if input_mgr.is_action_just_pressed("back") or input_mgr.is_action_just_pressed("pause"):
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")
            return

        all_buttons = [
            self.btn_prev_file, self.btn_next_file,
            self.btn_play_pause, self.btn_speed_slow, self.btn_speed_norm, self.btn_speed_fast,
            self.btn_back
        ]

        for btn in all_buttons:
            btn.check_hover(input_mgr.mouse_pos)
            if btn.is_hovered and input_mgr.mouse_just_pressed:
                self._handle_action(btn.action_id)

    def _handle_action(self, action_id: str):
        self.engine.audio_mgr.play_sfx("beep")
        if action_id == "prev_file":
            if self.saved_files:
                self.selected_file_idx = (self.selected_file_idx - 1) % len(self.saved_files)
                self._load_selected_file()
        elif action_id == "next_file":
            if self.saved_files:
                self.selected_file_idx = (self.selected_file_idx + 1) % len(self.saved_files)
                self._load_selected_file()
        elif action_id == "toggle_play":
            self.is_playing = not self.is_playing
            self.btn_play_pause.text = "PAUSE" if self.is_playing else "PLAY"
        elif action_id == "speed_0.5":
            self.playback_speed = 0.5
            self.engine.replay_mgr.playback_speed = 0.5
        elif action_id == "speed_1.0":
            self.playback_speed = 1.0
            self.engine.replay_mgr.playback_speed = 1.0
        elif action_id == "speed_2.0":
            self.playback_speed = 2.0
            self.engine.replay_mgr.playback_speed = 2.0
        elif action_id == "back":
            self.engine.state_mgr.change_state("title")

    def update(self, dt: float):
        if self.is_playing:
            has_more = self.engine.replay_mgr.advance_playback(dt)
            if not has_more:
                self.is_playing = False
                self.btn_play_pause.text = "PLAY"

    def render(self, surface: pygame.Surface):
        surface.fill((10, 14, 22))

        # Title
        t_s = self.font_title.render("SAVED REPLAY VIEWER", True, COLOR_GOLD)
        surface.blit(t_s, (VIRTUAL_WIDTH // 2 - t_s.get_width() // 2, 6))

        if not self.saved_files:
            no_s = self.font_mono.render("NO SAVED REPLAY FILES FOUND", True, (140, 150, 170))
            surface.blit(no_s, (VIRTUAL_WIDTH // 2 - no_s.get_width() // 2, VIRTUAL_HEIGHT // 2))
            self.btn_back.render(surface)
            return

        # Current File Header
        curr_file = self.saved_files[self.selected_file_idx]
        file_s = self.font_mono.render(f"{self.selected_file_idx+1}/{len(self.saved_files)}: {curr_file.name[:22]}", True, COLOR_CYAN)
        surface.blit(file_s, (VIRTUAL_WIDTH // 2 - file_s.get_width() // 2, 28))

        self.btn_prev_file.render(surface)
        self.btn_next_file.render(surface)

        # 1. World & Track Render
        frame_data = self.engine.replay_mgr.get_current_frame_data()
        if frame_data:
            px = frame_data.get("player_x", ROAD_CENTER_X)
            py = frame_data.get("player_y", 0.0)
            self.camera.update(0.016, px, py, 0.0)

            # Draw Road
            self.road_system.render(surface, self.camera, self.theme)

            # Draw Traffic
            for t_info in frame_data.get("traffic", []):
                tsx, tsy = self.camera.world_to_screen(t_info["x"], t_info["y"])
                spr = self.engine.asset_pipeline.get_surface(t_info.get("spr", "traffic_sedan_blue"), pygame)
                if spr:
                    surface.blit(spr, (tsx - spr.get_width() // 2, tsy - spr.get_height() // 2))

            # Draw Player
            psx, psy = self.camera.world_to_screen(px, py)
            car_spr = self.engine.replay_mgr.metadata.get("car_model", "player_red")
            sprite = self.engine.asset_pipeline.get_surface(car_spr, pygame)
            if sprite:
                surface.blit(sprite, (psx - sprite.get_width() // 2, psy - sprite.get_height() // 2))

        # 2. Timeline Scrubber Bar
        total_frames = len(self.engine.replay_mgr.frames)
        curr_frame = self.engine.replay_mgr.current_frame

        bar_x, bar_y, bar_w, bar_h = 20, VIRTUAL_HEIGHT - 54, VIRTUAL_WIDTH - 40, 6
        pygame.draw.rect(surface, (20, 25, 35), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surface, (60, 70, 90), (bar_x, bar_y, bar_w, bar_h), width=1)

        pct = (curr_frame / max(1, total_frames - 1))
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            pygame.draw.rect(surface, COLOR_CYAN, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.circle(surface, COLOR_GOLD, (bar_x + fill_w, bar_y + bar_h // 2), 4)

        # Telemetry HUD readout
        if frame_data:
            telemetry = f"FRAME: {curr_frame}/{total_frames} | SPEED: {int(frame_data.get('speed',0)/380*220)}KM/H | SCORE: {frame_data.get('score', 0)}"
            tel_s = self.font_mono.render(telemetry, True, COLOR_YELLOW)
            surface.blit(tel_s, (VIRTUAL_WIDTH // 2 - tel_s.get_width() // 2, VIRTUAL_HEIGHT - 65))

        # Control Buttons
        self.btn_play_pause.render(surface)
        self.btn_speed_slow.render(surface)
        self.btn_speed_norm.render(surface)
        self.btn_speed_fast.render(surface)
        self.btn_back.render(surface)
