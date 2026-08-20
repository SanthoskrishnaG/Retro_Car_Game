"""In-Game Track Level Editor State for designing and exporting custom circuits."""

from typing import List
import pygame

from retro_racer.engine.state_manager import State
from retro_racer.systems.level_editor import TrackData, TrackSegment
from retro_racer.ui.menu import MenuButton
from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_CYAN, COLOR_YELLOW,
    COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED,
    BIOME_CITY_DAY, BIOME_CITY_NIGHT, BIOME_SYNTHWAVE, BIOME_DESERT, BIOME_ALPINE
)


class EditorState(State):
    """Interactive visual track editor."""

    def __init__(self, engine):
        super().__init__(engine)
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 22)
        self.font_med = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 14)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New", 12, bold=True)

        self.biomes = [BIOME_CITY_DAY, BIOME_CITY_NIGHT, BIOME_SYNTHWAVE, BIOME_DESERT, BIOME_ALPINE]
        self.current_biome_idx = 0
        self.current_segment_idx = 0

        self.track_name = "Custom Speed Circuit"
        self.segments: List[TrackSegment] = [
            TrackSegment(length=1200.0, curve=0.0),
            TrackSegment(length=1400.0, curve=0.4),
            TrackSegment(length=1200.0, curve=-0.5),
            TrackSegment(length=1600.0, curve=0.0),
        ]

        self.status_msg = ""
        self.status_timer = 0.0

        self._init_buttons()

    def _init_buttons(self):
        cx = VIRTUAL_WIDTH // 2
        self.btn_biome = MenuButton(pygame.Rect(cx - 100, 60, 200, 28), "BIOME", "biome", font_size=13)

        # Segment Navigation
        self.btn_prev_seg = MenuButton(pygame.Rect(cx - 110, 100, 30, 28), "<", "prev_seg", font_size=14)
        self.btn_next_seg = MenuButton(pygame.Rect(cx + 80, 100, 30, 28), ">", "next_seg", font_size=14)

        # Segment Adjustments
        self.btn_curve_left = MenuButton(pygame.Rect(cx - 100, 140, 95, 28), "CURVE <", "curve_sub", font_size=12)
        self.btn_curve_right = MenuButton(pygame.Rect(cx + 5, 140, 95, 28), "CURVE >", "curve_add", font_size=12)

        self.btn_len_sub = MenuButton(pygame.Rect(cx - 100, 178, 95, 28), "-200m", "len_sub", font_size=12)
        self.btn_len_add = MenuButton(pygame.Rect(cx + 5, 178, 95, 28), "+200m", "len_add", font_size=12)

        # Add / Remove Segments
        self.btn_add_seg = MenuButton(pygame.Rect(cx - 100, 218, 95, 28), "+ ADD SEG", "add_seg", font_size=12, primary_color=COLOR_GREEN)
        self.btn_del_seg = MenuButton(pygame.Rect(cx + 5, 218, 95, 28), "- DEL SEG", "del_seg", font_size=12, primary_color=COLOR_RED)

        # Save & Back
        self.btn_save = MenuButton(pygame.Rect(cx - 100, VIRTUAL_HEIGHT - 90, 200, 34), "SAVE TRACK (JSON)", "save", font_size=14, primary_color=COLOR_GOLD)
        self.btn_back = MenuButton(pygame.Rect(cx - 100, VIRTUAL_HEIGHT - 48, 200, 34), "BACK TO MENU", "back", font_size=14, primary_color=COLOR_RED)

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler
        if input_mgr.is_action_just_pressed("back"):
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")
            return

        all_buttons = [
            self.btn_biome, self.btn_prev_seg, self.btn_next_seg,
            self.btn_curve_left, self.btn_curve_right,
            self.btn_len_sub, self.btn_len_add,
            self.btn_add_seg, self.btn_del_seg,
            self.btn_save, self.btn_back
        ]

        for btn in all_buttons:
            btn.check_hover(input_mgr.mouse_pos)
            if btn.is_hovered and input_mgr.mouse_just_pressed:
                self._handle_action(btn.action_id)

    def _handle_action(self, action_id: str):
        curr_seg = self.segments[self.current_segment_idx]
        self.engine.audio_mgr.play_sfx("beep")

        if action_id == "biome":
            self.current_biome_idx = (self.current_biome_idx + 1) % len(self.biomes)
        elif action_id == "prev_seg":
            self.current_segment_idx = (self.current_segment_idx - 1) % len(self.segments)
        elif action_id == "next_seg":
            self.current_segment_idx = (self.current_segment_idx + 1) % len(self.segments)
        elif action_id == "curve_sub":
            curr_seg.curve = max(-1.0, round(curr_seg.curve - 0.15, 2))
        elif action_id == "curve_add":
            curr_seg.curve = min(1.0, round(curr_seg.curve + 0.15, 2))
        elif action_id == "len_sub":
            curr_seg.length = max(400.0, curr_seg.length - 200.0)
        elif action_id == "len_add":
            curr_seg.length = min(4000.0, curr_seg.length + 200.0)
        elif action_id == "add_seg":
            self.segments.append(TrackSegment(length=1200.0, curve=0.0))
            self.current_segment_idx = len(self.segments) - 1
        elif action_id == "del_seg":
            if len(self.segments) > 1:
                self.segments.pop(self.current_segment_idx)
                self.current_segment_idx = max(0, self.current_segment_idx - 1)
        elif action_id == "save":
            track = TrackData(
                name=self.track_name,
                description="Custom Track created in Retro Racer Level Editor",
                biome=self.biomes[self.current_biome_idx],
                target_laps=1,
                difficulty="Custom",
                segments=self.segments
            )
            path = self.engine.level_editor.save_track(track)
            self.status_msg = f"SAVED: {path.name}"
            self.status_timer = 2.5
            self.engine.audio_mgr.play_sfx("coin")
        elif action_id == "back":
            self.engine.state_mgr.change_state("title")

    def update(self, dt: float):
        if self.status_timer > 0:
            self.status_timer -= dt

    def render(self, surface: pygame.Surface):
        surface.fill((14, 18, 28))

        # Title
        t_s = self.font_title.render("TRACK LEVEL EDITOR", True, COLOR_GOLD)
        surface.blit(t_s, (VIRTUAL_WIDTH // 2 - t_s.get_width() // 2, 16))

        # Biome Button & label
        biome_name = self.biomes[self.current_biome_idx].upper()
        self.btn_biome.text = f"BIOME: {biome_name}"
        self.btn_biome.render(surface)

        # Segment Selector
        seg_s = self.font_med.render(f"SEGMENT {self.current_segment_idx + 1} / {len(self.segments)}", True, COLOR_WHITE)
        surface.blit(seg_s, (VIRTUAL_WIDTH // 2 - seg_s.get_width() // 2, 106))
        self.btn_prev_seg.render(surface)
        self.btn_next_seg.render(surface)

        # Segment Details
        curr_seg = self.segments[self.current_segment_idx]
        curv_s = self.font_mono.render(f"Curvature: {curr_seg.curve:+.2f} ({'Straight' if curr_seg.curve == 0 else ('Right' if curr_seg.curve > 0 else 'Left')})", True, COLOR_CYAN)
        len_s = self.font_mono.render(f"Length: {curr_seg.length:.0f} px ({(curr_seg.length/50):.0f}m)", True, COLOR_YELLOW)
        surface.blit(curv_s, (VIRTUAL_WIDTH // 2 - curv_s.get_width() // 2, 126))
        self.btn_curve_left.render(surface)
        self.btn_curve_right.render(surface)

        surface.blit(len_s, (VIRTUAL_WIDTH // 2 - len_s.get_width() // 2, 164))
        self.btn_len_sub.render(surface)
        self.btn_len_add.render(surface)

        self.btn_add_seg.render(surface)
        self.btn_del_seg.render(surface)

        # Track Map Mini-Preview Box
        preview_rect = pygame.Rect(40, 260, VIRTUAL_WIDTH - 80, 240)
        pygame.draw.rect(surface, (20, 26, 40), preview_rect)
        pygame.draw.rect(surface, (0, 220, 255), preview_rect, width=1)

        p_lbl = self.font_mono.render("[TRACK PATH SCHEMATIC]", True, (160, 170, 190))
        surface.blit(p_lbl, (preview_rect.centerx - p_lbl.get_width() // 2, preview_rect.top + 6))

        # Draw wireframe schematic of road segments
        start_px, start_py = preview_rect.centerx, preview_rect.bottom - 20
        curr_px, curr_py = start_px, start_py

        for i, seg in enumerate(self.segments):
            seg_len_px = (seg.length / 4000.0) * 160.0
            next_px = curr_px + (seg.curve * 45.0)
            next_py = curr_py - seg_len_px

            col = COLOR_GOLD if i == self.current_segment_idx else COLOR_CYAN
            pygame.draw.line(surface, col, (int(curr_px), int(curr_py)), (int(next_px), int(next_py)), 4 if i == self.current_segment_idx else 2)
            pygame.draw.circle(surface, COLOR_WHITE, (int(next_px), int(next_py)), 3)

            curr_px, curr_py = next_px, next_py

        # Status notification
        if self.status_timer > 0:
            st_s = self.font_mono.render(self.status_msg, True, COLOR_GREEN)
            surface.blit(st_s, (VIRTUAL_WIDTH // 2 - st_s.get_width() // 2, VIRTUAL_HEIGHT - 116))

        self.btn_save.render(surface)
        self.btn_back.render(surface)
