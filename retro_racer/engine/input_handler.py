"""Unified, ultra-responsive input manager with continuous polling and configurable keybindings."""

import json
from pathlib import Path
from typing import Dict, Set, Tuple, List, Optional
import pygame

from retro_racer.config import KEYBINDINGS_FILE, DEFAULT_KEYBINDINGS


class InputHandler:
    """Processes input events, polls continuous key states, and manages configurable keybindings."""

    def __init__(self):
        self.held_keys: Set[int] = set()
        self.pressed_keys: Set[int] = set()
        self.released_keys: Set[int] = set()
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_clicked: bool = False
        self.mouse_just_pressed: bool = False

        # Continuous action floats / booleans
        self.steer: float = 0.0
        self.throttle: bool = False
        self.brake: bool = False
        self.nitro: bool = False

        # Rebinding state
        self.rebinding_action: Optional[str] = None

        # Keybindings dictionary
        self.keybindings: Dict[str, List[int]] = {}
        self.load_keybindings()

        # Controller / Joystick
        self.joystick = None
        self._init_joysticks()

    def _init_joysticks(self):
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            try:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            except Exception:
                self.joystick = None

    def load_keybindings(self):
        """Load keybindings from JSON or apply defaults."""
        if KEYBINDINGS_FILE.exists():
            try:
                with open(KEYBINDINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.keybindings = {k: v for k, v in data.items()}
                # Ensure all default keys exist
                for action, keys in DEFAULT_KEYBINDINGS.items():
                    if action not in self.keybindings:
                        self.keybindings[action] = list(keys)
                return
            except Exception:
                pass
        self.keybindings = {k: list(v) for k, v in DEFAULT_KEYBINDINGS.items()}

    def save_keybindings(self):
        """Persist current keybindings to JSON."""
        try:
            with open(KEYBINDINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.keybindings, f, indent=2)
        except Exception:
            pass

    def rebind_action(self, action: str, new_key: int):
        """Set a single primary key code for an action."""
        if action in self.keybindings:
            self.keybindings[action] = [new_key]
            self.save_keybindings()

    def get_key_name(self, action: str) -> str:
        """Get human-readable name of primary bound key for action."""
        keys = self.keybindings.get(action, [])
        if not keys:
            return "NONE"
        key_code = keys[0]
        return pygame.key.name(key_code).upper()

    def begin_frame(self):
        """Reset per-frame single-press event registers."""
        self.pressed_keys.clear()
        self.released_keys.clear()
        self.mouse_just_pressed = False

    def process_event(self, event: pygame.event.Event, scale: float = 1.0):
        """Process a single Pygame event."""
        if event.type == pygame.KEYDOWN:
            self.held_keys.add(event.key)
            self.pressed_keys.add(event.key)
            # Check if currently rebinding
            if self.rebinding_action:
                self.rebind_action(self.rebinding_action, event.key)
                self.rebinding_action = None
        elif event.type == pygame.KEYUP:
            self.held_keys.discard(event.key)
            self.released_keys.add(event.key)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = (int(event.pos[0] / scale), int(event.pos[1] / scale))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_clicked = True
                self.mouse_just_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_clicked = False

    def update_continuous_actions(self):
        """Poll continuous keyboard state with zero input lag."""
        # Use continuous hardware key state array
        keys_pressed = pygame.key.get_pressed()

        def is_action_held(action: str) -> bool:
            for k in self.keybindings.get(action, []):
                if k < len(keys_pressed) and keys_pressed[k]:
                    return True
            return False

        left = is_action_held("steer_left")
        right = is_action_held("steer_right")
        up = is_action_held("accelerate")
        down = is_action_held("brake")
        space = is_action_held("nitro")

        # Smooth analog-like responsive steering
        if left and not right:
            self.steer = -1.0
        elif right and not left:
            self.steer = 1.0
        else:
            self.steer = 0.0

        self.throttle = up
        self.brake = down
        self.nitro = space

        # Gamepad Analog Override
        if self.joystick:
            try:
                axis_x = self.joystick.get_axis(0)
                if abs(axis_x) > 0.15:
                    self.steer = axis_x
                if self.joystick.get_button(0):  # A button
                    self.throttle = True
                if self.joystick.get_button(1):  # B button
                    self.brake = True
                if self.joystick.get_button(2) or self.joystick.get_button(5):  # X or R-Trigger
                    self.nitro = True
            except Exception:
                pass

    def is_action_just_pressed(self, action: str) -> bool:
        """Check if any key bound to an action was pressed down this frame."""
        for k in self.keybindings.get(action, []):
            if k in self.pressed_keys:
                return True
        return False

    def is_just_pressed(self, key_code: int) -> bool:
        """Direct key check."""
        return key_code in self.pressed_keys
