"""Garage State for vehicle selection and upgrading performance stats."""

import pygame

from retro_racer.engine.state_manager import State
from retro_racer.ui.garage import GarageUI
from retro_racer.ui.menu import MenuButton
from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, COLOR_CYAN, COLOR_YELLOW,
    COLOR_GREEN, COLOR_RED, COLOR_WHITE
)


class GarageState(State):
    """Interactive showroom for upgrading car specs and choosing custom paint/models."""

    def __init__(self, engine):
        super().__init__(engine)
        self.ui = GarageUI()
        self.profile = {}
        self.buttons = []
        self.selected_btn_idx = 0
        self._init_buttons()

    def _init_buttons(self):
        self.buttons = [
            # Upgrade buttons 0 to 4
            MenuButton(pygame.Rect(VIRTUAL_WIDTH - 120, 236 + (i * 52), 80, 30), "UPGRADE", f"up_{up[0]}", font_size=12)
            for i, up in enumerate(self.ui.upgrade_defs)
        ]
        # Car cycle buttons & back button
        self.btn_prev_car = MenuButton(pygame.Rect(36, 126, 32, 32), "<", "prev_car", font_size=16)
        self.btn_next_car = MenuButton(pygame.Rect(VIRTUAL_WIDTH - 68, 126, 32, 32), ">", "next_car", font_size=16)
        self.btn_select_car = MenuButton(pygame.Rect(VIRTUAL_WIDTH // 2 - 60, 185, 120, 28), "EQUIP / BUY", "equip", font_size=13, primary_color=COLOR_GREEN)
        self.btn_back = MenuButton(pygame.Rect(VIRTUAL_WIDTH // 2 - 80, VIRTUAL_HEIGHT - 45, 160, 32), "BACK TO MENU", "back", font_size=14, primary_color=COLOR_RED)

    def on_enter(self, **kwargs):
        self._reload_profile()
        selected_car = self.profile.get("selected_car", "player_red")
        for i, (cid, _, _) in enumerate(self.ui.cars):
            if cid == selected_car:
                self.ui.selected_car_idx = i
                break

    def _reload_profile(self):
        self.profile = self.engine.db.get_career_profile()

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler

        if input_mgr.is_action_just_pressed("back"):
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")
            return

        # Car carousel navigation
        if input_mgr.is_action_just_pressed("left"):
            self._cycle_car(-1)
        elif input_mgr.is_action_just_pressed("right"):
            self._cycle_car(1)

        # Mouse clicks on buttons
        all_interactive = self.buttons + [self.btn_prev_car, self.btn_next_car, self.btn_select_car, self.btn_back]
        for btn in all_interactive:
            btn.check_hover(input_mgr.mouse_pos)
            if btn.is_hovered and input_mgr.mouse_just_pressed:
                self._handle_action(btn.action_id)

    def _cycle_car(self, direction: int):
        self.ui.selected_car_idx = (self.ui.selected_car_idx + direction) % len(self.ui.cars)
        self.engine.audio_mgr.play_sfx("beep")

    def _handle_action(self, action_id: str):
        car_id, car_name, unlock_cost = self.ui.cars[self.ui.selected_car_idx]
        is_unlocked = self.engine.db.is_car_unlocked(car_id)

        if action_id == "prev_car":
            self._cycle_car(-1)
        elif action_id == "next_car":
            self._cycle_car(1)
        elif action_id == "equip":
            if is_unlocked:
                self.engine.db.select_car(car_id)
                self.engine.audio_mgr.play_sfx("coin")
            else:
                # Attempt unlock
                if self.engine.db.unlock_car(car_id, unlock_cost):
                    self.engine.db.select_car(car_id)
                    self.engine.audio_mgr.play_sfx("pickup")
                else:
                    self.engine.audio_mgr.play_sfx("crash", volume_scale=0.3)
            self._reload_profile()
        elif action_id.startswith("up_"):
            up_type = action_id[3:]
            # Calculate cost
            for ut, _, base_cost in self.ui.upgrade_defs:
                if ut == up_type:
                    curr_lvl = self.profile.get(f"upgrade_{ut}", 0)
                    cost = base_cost * (curr_lvl + 1)
                    if self.engine.db.purchase_upgrade(up_type, cost):
                        self.engine.audio_mgr.play_sfx("coin")
                        self._reload_profile()
                    else:
                        self.engine.audio_mgr.play_sfx("crash", volume_scale=0.3)
                    break
        elif action_id == "back":
            self.engine.audio_mgr.play_sfx("beep")
            self.engine.state_mgr.change_state("title")

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        car_id, _, _ = self.ui.cars[self.ui.selected_car_idx]
        is_unlocked = self.engine.db.is_car_unlocked(car_id)
        selected_car = self.profile.get("selected_car", "player_red")

        self.ui.render(surface, self.profile, self.engine.asset_pipeline, is_unlocked, selected_car)

        # Draw buttons
        self.btn_prev_car.render(surface)
        self.btn_next_car.render(surface)
        self.btn_select_car.render(surface)
        self.btn_back.render(surface)

        for btn in self.buttons:
            btn.render(surface)
