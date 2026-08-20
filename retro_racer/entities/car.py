"""Base vehicle class defining physics, velocity properties, collision bounding, and rendering."""

import math
from typing import Tuple, Optional
import pygame

from retro_racer.config import (
    COLOR_WHITE, ROAD_LEFT_EDGE, ROAD_RIGHT_EDGE,
    PLAYER_OFFROAD_DECEL, PLAYER_OFFROAD_MAX_SPEED
)


class BaseCar:
    """Base class for player and AI traffic vehicles with physics state."""

    def __init__(self, x: float, y: float, width: int = 24, height: int = 44, sprite_name: str = "player_red"):
        # Explicit vehicle position properties
        self.position_x: float = float(x)
        self.position_y: float = float(y)

        # Explicit vehicle velocity properties
        self.velocity_x: float = 0.0
        self.velocity_y: float = 0.0

        # Dynamics
        self.speed: float = 0.0
        self.max_speed: float = 380.0
        self.acceleration: float = 220.0
        self.braking_force: float = 380.0
        self.friction: float = 90.0
        self.steering_speed: float = 240.0
        self.drift_factor: float = 0.86

        # Dimensions & Sprite
        self.width = width
        self.height = height
        self.sprite_name = sprite_name

        # State & Combat
        self.health: float = 100.0
        self.max_health: float = 100.0
        self.fuel: float = 100.0
        self.nitro: float = 60.0
        self.score: int = 0
        self.is_crashed: bool = False
        self.spin_timer: float = 0.0
        self.turn_tilt: float = 0.0

    # Properties to allow access via .x and .y seamlessly
    @property
    def x(self) -> float:
        return self.position_x

    @x.setter
    def x(self, val: float):
        self.position_x = float(val)

    @property
    def y(self) -> float:
        return self.position_y

    @y.setter
    def y(self, val: float):
        self.position_y = float(val)

    def get_hitbox(self) -> pygame.Rect:
        """Returns collision bounding box with a small margin for arcade feel."""
        margin_x = 3
        margin_y = 4
        return pygame.Rect(
            int(self.position_x - (self.width - margin_x * 2) / 2),
            int(self.position_y - (self.height - margin_y * 2) / 2),
            self.width - margin_x * 2,
            self.height - margin_y * 2
        )

    def get_near_miss_hitbox(self, margin: float = 18.0) -> pygame.Rect:
        """Larger hitbox to detect near-miss overtakes."""
        return pygame.Rect(
            int(self.position_x - (self.width / 2 + margin)),
            int(self.position_y - (self.height / 2 + margin)),
            int(self.width + margin * 2),
            int(self.height + margin * 2)
        )

    def is_offroad(self, road_left: float = ROAD_LEFT_EDGE, road_right: float = ROAD_RIGHT_EDGE) -> bool:
        """Check if vehicle is driving outside the asphalt."""
        half_w = self.width / 2
        return (self.position_x - half_w < road_left) or (self.position_x + half_w > road_right)

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
        sx, sy = camera.world_to_screen(self.position_x, self.position_y)

        # Off-screen culling
        if sy < -100 or sy > camera.height + 100 or sx < -100 or sx > camera.width + 100:
            return

        sprite = asset_pipeline.get_surface(self.sprite_name, pygame)
        if sprite is None:
            rect = pygame.Rect(sx - self.width // 2, sy - self.height // 2, self.width, self.height)
            pygame.draw.rect(surface, (200, 40, 40), rect)
            return

        # Apply turn tilting / spinning
        tilt = self.turn_tilt
        if self.spin_timer <= 0:
            tilt = max(-15.0, min(15.0, -self.velocity_x / max(1.0, self.steering_speed) * 12.0))

        if abs(tilt) > 1.0:
            rotated = pygame.transform.rotate(sprite, tilt)
            rot_rect = rotated.get_rect(center=(sx, sy))
            surface.blit(rotated, rot_rect)
        else:
            surface.blit(sprite, (sx - self.width // 2, sy - self.height // 2))

        # Brake lights glow
        if is_braking:
            glow_rect = pygame.Rect(sx - 8, sy + self.height // 2 - 4, 16, 3)
            glow_surf = pygame.Surface((16, 3), pygame.SRCALPHA)
            glow_surf.fill((255, 30, 30, 180))
            surface.blit(glow_surf, (sx - 8, sy + self.height // 2 - 4))
