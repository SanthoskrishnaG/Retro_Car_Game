"""Settings, Display Scaling, and Interactive Key Rebinding State."""

from typing import List, Tuple
import pygame

from retro_racer.engine.state_manager import State
from retro_racer.ui.menu import MenuButton
from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_CYAN, COLOR_YELLOW,
    COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED
)


class SettingsState(State):
    """Configuration menu with interactive key rebinding and resolution scale selectors."""

    def __init__(self, engine):
        super().__init__(engine)
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 16)
        self.font_med = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 12)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New", 10, bold=True)

        self.scale_options = [1.0, 2.0, 3.0, 4.0]
        self.current_scale_idx = 2  # default 3.0x (960x720)

        # Tab: "general" or "controls"
        self.active_tab = "general"

        # Rebindable action keys
        self.rebind_actions = [
            ("accelerate", "Accelerate"),
            ("brake", "Brake / Rev"),
            ("steer_left", "Steer Left"),
            ("steer_right", "Steer Right"),
            ("nitro", "Nitro Boost"),
            ("pause", "Pause Game"),
            ("restart", "Restart Race"),
            ("mute", "Mute Audio"),
        ]

        self.buttons = []
        self._init_buttons()

    def _init_buttons(self):
        cx = VIRTUAL_WIDTH // 2
        # Tab Buttons
        self.btn_tab_gen = MenuButton(pygame.Rect(cx - 95, 34, 90, 22), "GENERAL", "tab_gen", font_size=10, primary_color=COLOR_CYAN)
        self.btn_tab_ctrl = MenuButton(pygame.Rect(cx + 5, 34, 90, 22), "CONTROLS", "tab_ctrl", font_size=10, primary_color=COLOR_YELLOW)

        # General Options
        self.btn_scale = MenuButton(pygame.Rect(cx - 95, 66, 190, 24), "SCALE: 3X (960x720)", "cycle_scale", font_size=11)
        self.btn_fullscreen = MenuButton(pygame.Rect(cx - 95, 96, 190, 24), "FULLSCREEN: OFF", "toggle_fs", font_size=11)
        self.btn_crt = MenuButton(pygame.Rect(cx - 95, 126, 190, 24), "CRT SCANLINES: ON", "toggle_crt", font_size=11)
        self.btn_vol_master = MenuButton(pygame.Rect(cx - 95, 156, 190, 24), "MASTER VOL: 80%", "vol_master", font_size=11)

        # Control Rebind Buttons (2 columns of 4)
        self.rebind_buttons = []
        for i, (act, name) in enumerate(self.rebind_actions):
            col = i % 2
            row = i // 2
            bx = 20 if col == 0 else 170
            by = 66 + (row * 32)
            btn = MenuButton(pygame.Rect(bx, by, 130, 26), f"{name}: ...", f"rebind_{act}", font_size=10)
            self.rebind_buttons.append(btn)

        # Back Button
        self.btn_back = MenuButton(pygame.Rect(cx - 65, VIRTUAL_HEIGHT - 28, 130, 22), "BACK TO MENU", "back", font_size=11, primary_color=COLOR_RED)

    def on_enter(self, **kwargs):
        self._refresh_labels()

    def _refresh_labels(self):
        input_mgr = self.engine.input_handler
        # Refresh Scale label
        if self.engine.is_fullscreen:
            self.btn_scale.text = "SCALE: FULLSCREEN"
            self.btn_fullscreen.text = "FULLSCREEN: ON"
        else:
            cur_s = self.scale_options[self.current_scale_idx]
            w, h = int(320 * cur_s), int(240 * cur_s)
            self.btn_scale.text = f"SCALE: {int(cur_s)}X ({w}x{h})"
            self.btn_fullscreen.text = "FULLSCREEN: OFF"

        self.btn_crt.text = f"CRT SCANLINES: {'ON' if self.engine.renderer.enable_crt else 'OFF'}"

        # Refresh Rebind Buttons
        for i, (act, name) in enumerate(self.rebind_actions):
            key_name = input_mgr.get_key_name(act)
            if input_mgr.rebinding_action == act:
                self.rebind_buttons[i].text = f"{name}: [PRESS KEY]"
            else:
                self.rebind_buttons[i].text = f"{name}: [{key_name}]"

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler

        # If rebinding, any keypress completes the rebinding
        if input_mgr.rebinding_action:
            self._refresh_labels()
            return

        if input_mgr.is_action_just_pressed("back"):
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")
            return

        # Check clicks
        active_list = [self.btn_tab_gen, self.btn_tab_ctrl, self.btn_back]
        if self.active_tab == "general":
            active_list += [self.btn_scale, self.btn_fullscreen, self.btn_crt, self.btn_vol_master]
        else:
            active_list += self.rebind_buttons

        for btn in active_list:
            btn.check_hover(input_mgr.mouse_pos)
            if btn.is_hovered and input_mgr.mouse_just_pressed:
                self._handle_action(btn.action_id)

    def _handle_action(self, action_id: str):
        self.engine.audio_mgr.play_sfx("beep")
        input_mgr = self.engine.input_handler

        if action_id == "tab_gen":
            self.active_tab = "general"
        elif action_id == "tab_ctrl":
            self.active_tab = "controls"
            self._refresh_labels()
        elif action_id == "cycle_scale":
            self.current_scale_idx = (self.current_scale_idx + 1) % len(self.scale_options)
            scale = self.scale_options[self.current_scale_idx]
            self.engine.set_display_scale(scale)
            self._refresh_labels()
        elif action_id == "toggle_fs":
            self.engine.toggle_fullscreen()
            self._refresh_labels()
        elif action_id == "toggle_crt":
            self.engine.renderer.enable_crt = not self.engine.renderer.enable_crt
            self._refresh_labels()
        elif action_id == "vol_master":
            self.engine.audio_mgr.master_volume = (self.engine.audio_mgr.master_volume + 0.25) % 1.25
            if self.engine.audio_mgr.master_volume < 0.1:
                self.engine.audio_mgr.master_volume = 0.0
            pct = int(self.engine.audio_mgr.master_volume * 100)
            self.btn_vol_master.text = f"MASTER VOL: {pct}%"
        elif action_id.startswith("rebind_"):
            act = action_id[7:]
            input_mgr.rebinding_action = act
            self._refresh_labels()
        elif action_id == "back":
            self.engine.state_mgr.change_state("title")

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.fill((12, 16, 26))

        # Title
        t_s = self.font_title.render("CONFIGURATION & SETTINGS", True, COLOR_GOLD)
        surface.blit(t_s, (VIRTUAL_WIDTH // 2 - t_s.get_width() // 2, 10))

        # Tabs
        self.btn_tab_gen.is_selected = (self.active_tab == "general")
        self.btn_tab_ctrl.is_selected = (self.active_tab == "controls")
        self.btn_tab_gen.render(surface)
        self.btn_tab_ctrl.render(surface)

        if self.active_tab == "general":
            self.btn_scale.render(surface)
            self.btn_fullscreen.render(surface)
            self.btn_crt.render(surface)
            self.btn_vol_master.render(surface)
        else:
            hint_s = self.font_mono.render("Click an action, then press key to rebind:", True, COLOR_CYAN)
            surface.blit(hint_s, (VIRTUAL_WIDTH // 2 - hint_s.get_width() // 2, 54))
            for btn in self.rebind_buttons:
                btn.render(surface)

        self.btn_back.render(surface)
