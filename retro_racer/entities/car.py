"""Base vehicle class defining physics, collision bounding, and rendering."""

import math
from typing import Tuple, Optional
import pygame

from retro_racer.config import (
    COLOR_WHITE, ROAD_LEFT_EDGE, ROAD_RIGHT_EDGE,
    PLAYER_OFFROAD_DECEL, PLAYER_OFFROAD_MAX_SPEED
)


class BaseCar:
    """Base class for player and AI traffic cars."""

    def __init__(self, x: float, y: float, width: int = 34, height: int = 62, sprite_name: str = "player_red"):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.sprite_name = sprite_name

        # Physics
        self.speed = 0.0              # Forward speed (px/s)
        self.lateral_speed = 0.0      # Horizontal velocity (px/s)
        self.max_speed = 450.0
        self.acceleration = 250.0
        self.braking = 400.0
        self.drift_factor = 0.88
        self.steer_speed = 280.0

        # State
        self.health = 100.0
        self.max_health = 100.0
        self.is_crashed = False
        self.spin_timer = 0.0         # Seconds remaining in oil spin
        self.turn_tilt = 0.0          # Angular tilt in degrees (-12 to +12)

    def get_hitbox(self) -> pygame.Rect:
        """Returns collision bounding box with a small margin for arcade feel."""
        margin_x = 4
        margin_y = 6
        return pygame.Rect(
            int(self.x - (self.width - margin_x * 2) / 2),
            int(self.y - (self.height - margin_y * 2) / 2),
            self.width - margin_x * 2,
            self.height - margin_y * 2
        )

    def get_near_miss_hitbox(self, margin: float = 24.0) -> pygame.Rect:
        """Larger hitbox to detect near-miss overtakes."""
        return pygame.Rect(
            int(self.x - (self.width / 2 + margin)),
            int(self.y - (self.height / 2 + margin)),
            int(self.width + margin * 2),
            int(self.height + margin * 2)
        )

    def is_offroad(self, road_left: float = ROAD_LEFT_EDGE, road_right: float = ROAD_RIGHT_EDGE) -> bool:
        """Check if vehicle is driving outside the asphalt."""
        half_w = self.width / 2
        return (self.x - half_w < road_left) or (self.x + half_w > road_right)

    def apply_oil_spin(self, duration: float = 1.2):
        """Trigger an involuntary spin-out when hitting an oil slick."""
        self.spin_timer = duration
        self.speed *= 0.65

    def update_spin(self, dt: float):
        """Update spin-out timer and angle."""
        if self.spin_timer > 0:
            self.spin_timer -= dt
            self.turn_tilt += 720.0 * dt  # rapid 360 spin
        else:
            self.spin_timer = 0.0

    def render(self, surface: pygame.Surface, camera, asset_pipeline, is_braking: bool = False):
        """Draw car sprite with camera transform and rotation banking."""
        sx, sy = camera.world_to_screen(self.x, self.y)

        # Off-screen culling
        if sy < -100 or sy > camera.height + 100 or sx < -100 or sx > camera.width + 100:
            return

        sprite = asset_pipeline.get_surface(self.sprite_name, pygame)
        if sprite is None:
            # Fallback rectangle
            rect = pygame.Rect(sx - self.width // 2, sy - self.height // 2, self.width, self.height)
            pygame.draw.rect(surface, (200, 40, 40), rect)
            return

        # Apply turn tilting / spinning
        tilt = self.turn_tilt
        if self.spin_timer <= 0:
            # Smoothly bank car into turns
            tilt = max(-15.0, min(15.0, -self.lateral_speed / self.steer_speed * 12.0))

        if abs(tilt) > 1.0:
            rotated = pygame.transform.rotate(sprite, tilt)
            rot_rect = rotated.get_rect(center=(sx, sy))
            surface.blit(rotated, rot_rect)
        else:
            surface.blit(sprite, (sx - self.width // 2, sy - self.height // 2))

        # Brake lights glow
        if is_braking:
            glow_rect = pygame.Rect(sx - 12, sy + self.height // 2 - 6, 24, 4)
            glow_surf = pygame.Surface((24, 6), pygame.SRCALPHA)
            glow_surf.fill((255, 30, 30, 180))
            surface.blit(glow_surf, (sx - 12, sy + self.height // 2 - 6))
