"""Settings and Keybindings Configuration State."""

import pygame

from retro_racer.engine.state_manager import State
from retro_racer.ui.menu import MenuButton
from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_CYAN, COLOR_YELLOW,
    COLOR_WHITE, COLOR_GOLD, COLOR_GREEN, COLOR_RED
)


class SettingsState(State):
    """Audio, Video, and Controls configuration screen."""

    def __init__(self, engine):
        super().__init__(engine)
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 22)
        self.font_med = pygame.font.SysFont("Impact, Arial Black, Trebuchet MS", 14)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New", 12, bold=True)

        self.buttons = []
        self._init_buttons()

    def _init_buttons(self):
        cx = VIRTUAL_WIDTH // 2
        self.btn_crt = MenuButton(pygame.Rect(cx - 100, 75, 200, 32), "CRT SCANLINES: ON", "toggle_crt", font_size=13)
        self.btn_vol_master = MenuButton(pygame.Rect(cx - 100, 118, 200, 32), "MASTER VOL: 80%", "vol_master", font_size=13)
        self.btn_vol_sfx = MenuButton(pygame.Rect(cx - 100, 161, 200, 32), "SFX VOL: 85%", "vol_sfx", font_size=13)
        self.btn_vol_music = MenuButton(pygame.Rect(cx - 100, 204, 200, 32), "MUSIC VOL: 65%", "vol_music", font_size=13)
        self.btn_back = MenuButton(pygame.Rect(cx - 80, VIRTUAL_HEIGHT - 45, 160, 32), "BACK TO MENU", "back", font_size=14, primary_color=COLOR_RED)

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler
        if input_mgr.is_action_just_pressed("back"):
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")
            return

        all_buttons = [self.btn_crt, self.btn_vol_master, self.btn_vol_sfx, self.btn_vol_music, self.btn_back]
        for btn in all_buttons:
            btn.check_hover(input_mgr.mouse_pos)
            if btn.is_hovered and input_mgr.mouse_just_pressed:
                self._handle_action(btn.action_id)

    def _handle_action(self, action_id: str):
        self.engine.audio_mgr.play_sfx("beep")
        if action_id == "toggle_crt":
            self.engine.renderer.enable_crt = not self.engine.renderer.enable_crt
            self.btn_crt.text = f"CRT SCANLINES: {'ON' if self.engine.renderer.enable_crt else 'OFF'}"
        elif action_id == "vol_master":
            self.engine.audio_mgr.master_volume = (self.engine.audio_mgr.master_volume + 0.2) % 1.2
            if self.engine.audio_mgr.master_volume < 0.1:
                self.engine.audio_mgr.master_volume = 0.0
            pct = int(self.engine.audio_mgr.master_volume * 100)
            self.btn_vol_master.text = f"MASTER VOL: {pct}%"
        elif action_id == "vol_sfx":
            self.engine.audio_mgr.sfx_volume = (self.engine.audio_mgr.sfx_volume + 0.2) % 1.2
            if self.engine.audio_mgr.sfx_volume < 0.1:
                self.engine.audio_mgr.sfx_volume = 0.0
            pct = int(self.engine.audio_mgr.sfx_volume * 100)
            self.btn_vol_sfx.text = f"SFX VOL: {pct}%"
        elif action_id == "vol_music":
            self.engine.audio_mgr.music_volume = (self.engine.audio_mgr.music_volume + 0.2) % 1.2
            if self.engine.audio_mgr.music_volume < 0.1:
                self.engine.audio_mgr.music_volume = 0.0
            pct = int(self.engine.audio_mgr.music_volume * 100)
            self.btn_vol_music.text = f"MUSIC VOL: {pct}%"
            if self.engine.audio_mgr.music_sound:
                self.engine.audio_mgr.music_sound.set_volume(self.engine.audio_mgr.master_volume * self.engine.audio_mgr.music_volume)
        elif action_id == "back":
            self.engine.state_mgr.change_state("title")

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.fill((12, 16, 26))

        # Title
        t_s = self.font_title.render("SETTINGS & CONTROLS", True, COLOR_GOLD)
        surface.blit(t_s, (VIRTUAL_WIDTH // 2 - t_s.get_width() // 2, 20))

        # Buttons
        self.btn_crt.render(surface)
        self.btn_vol_master.render(surface)
        self.btn_vol_sfx.render(surface)
        self.btn_vol_music.render(surface)

        # Controls Guide Card
        card_rect = pygame.Rect(30, 256, VIRTUAL_WIDTH - 60, 230)
        pygame.draw.rect(surface, (18, 24, 38), card_rect)
        pygame.draw.rect(surface, (0, 220, 255), card_rect, width=1)

        c_title = self.font_med.render("ARCADE CONTROLS GUIDE", True, COLOR_CYAN)
        surface.blit(c_title, (card_rect.centerx - c_title.get_width() // 2, card_rect.top + 10))
        pygame.draw.line(surface, (50, 60, 80), (card_rect.left + 16, card_rect.top + 34), (card_rect.right - 16, card_rect.top + 34), 1)

        controls = [
            ("Steer Left / Right:", "A / D or LEFT / RIGHT"),
            ("Accelerate Throttle:", "W or UP ARROW"),
            ("Brake / Reverse:", "S or DOWN ARROW"),
            ("Nitro Boost Thrust:", "SPACEBAR or LEFT SHIFT"),
            ("Pause Game:", "ESCAPE or P KEY"),
            ("Developer Tools:", "F3 DEBUG OVERLAY"),
            ("God Mode / Cheats:", "G (God) / N (Inf Nitro) in F3"),
        ]

        y = card_rect.top + 46
        for action, binding in controls:
            act_s = self.font_mono.render(action, True, (170, 180, 200))
            bind_s = self.font_mono.render(binding, True, COLOR_YELLOW)
            surface.blit(act_s, (card_rect.left + 14, y))
            surface.blit(bind_s, (card_rect.left + 175, y))
            y += 24

        self.btn_back.render(surface)
