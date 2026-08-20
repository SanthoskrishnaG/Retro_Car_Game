"""Unified input management supporting keyboard and joystick/gamepads."""

from typing import Dict, Set, Tuple
import pygame


class InputHandler:
    """Processes input events and maintains action states."""

    def __init__(self):
        self.held_keys: Set[int] = set()
        self.pressed_keys: Set[int] = set()
        self.released_keys: Set[int] = set()
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_clicked: bool = False
        self.mouse_just_pressed: bool = False

        # Continuous actions
        self.steer: float = 0.0
        self.throttle: bool = False
        self.brake: bool = False
        self.nitro: bool = False

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
        """Compute analog-like steering, throttle, brake, and nitro values."""
        left = (pygame.K_LEFT in self.held_keys) or (pygame.K_a in self.held_keys)
        right = (pygame.K_RIGHT in self.held_keys) or (pygame.K_d in self.held_keys)
        up = (pygame.K_UP in self.held_keys) or (pygame.K_w in self.held_keys)
        down = (pygame.K_DOWN in self.held_keys) or (pygame.K_s in self.held_keys)
        space = (pygame.K_SPACE in self.held_keys) or (pygame.K_LSHIFT in self.held_keys)

        # Keyboard Steer
        if left and not right:
            self.steer = -1.0
        elif right and not left:
            self.steer = 1.0
        else:
            self.steer = 0.0

        self.throttle = up
        self.brake = down
        self.nitro = space

        # Joystick override if available
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

    def is_just_pressed(self, key_code: int) -> bool:
        """Check if key was pressed this frame."""
        return key_code in self.pressed_keys

    def is_action_just_pressed(self, action: str) -> bool:
        """Helper for checking common actions."""
        if action == "pause":
            return self.is_just_pressed(pygame.K_ESCAPE) or self.is_just_pressed(pygame.K_p)
        elif action == "confirm":
            return self.is_just_pressed(pygame.K_RETURN) or self.is_just_pressed(pygame.K_SPACE)
        elif action == "back":
            return self.is_just_pressed(pygame.K_ESCAPE) or self.is_just_pressed(pygame.K_BACKSPACE)
        elif action == "up":
            return self.is_just_pressed(pygame.K_UP) or self.is_just_pressed(pygame.K_w)
        elif action == "down":
            return self.is_just_pressed(pygame.K_DOWN) or self.is_just_pressed(pygame.K_s)
        elif action == "left":
            return self.is_just_pressed(pygame.K_LEFT) or self.is_just_pressed(pygame.K_a)
        elif action == "right":
            return self.is_just_pressed(pygame.K_RIGHT) or self.is_just_pressed(pygame.K_d)
        elif action == "debug":
            return self.is_just_pressed(pygame.K_F3)
        return False
