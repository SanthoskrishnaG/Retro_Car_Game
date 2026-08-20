"""Power-up pickups, collectibles, and road hazards."""

import math
from enum import Enum
from typing import Tuple, Optional
import pygame

from retro_racer.config import (
    FUEL_PICKUP_AMOUNT, COIN_SCORE, COLOR_YELLOW, COLOR_CYAN, COLOR_GREEN
)


class PickupType(Enum):
    FUEL = "fuel"
    NITRO = "nitro"
    COIN = "coin"
    SHIELD = "shield"
    MAGNET = "magnet"
    SLOWMO = "slowmo"
    MULTIPLIER_2X = "2x"
    WRENCH = "wrench"


class HazardType(Enum):
    OIL_SLICK = "oil"
    ROAD_CONE = "cone"


class Pickup:
    """Collectible item that grants power-up bonuses."""

    def __init__(self, x: float, y: float, pickup_type: PickupType):
        self.x = float(x)
        self.y = float(y)
        self.pickup_type = pickup_type
        self.is_collected = False
        self.width = 26
        self.height = 26

        # Map type to sprite & amounts
        if pickup_type == PickupType.FUEL:
            self.sprite_name = "pickup_fuel"
            self.amount = FUEL_PICKUP_AMOUNT
        elif pickup_type == PickupType.NITRO:
            self.sprite_name = "pickup_nitro"
            self.amount = 40.0
        elif pickup_type == PickupType.COIN:
            self.sprite_name = "pickup_coin"
            self.amount = COIN_SCORE
        elif pickup_type == PickupType.SHIELD:
            self.sprite_name = "pickup_shield"
            self.amount = 1.0
        elif pickup_type == PickupType.MAGNET:
            self.sprite_name = "pickup_magnet"
            self.amount = 1.0
        elif pickup_type == PickupType.SLOWMO:
            self.sprite_name = "pickup_slowmo"
            self.amount = 1.0
        elif pickup_type == PickupType.MULTIPLIER_2X:
            self.sprite_name = "pickup_2x"
            self.amount = 1.0
        elif pickup_type == PickupType.WRENCH:
            self.sprite_name = "pickup_wrench"
            self.amount = 35.0
        else:
            self.sprite_name = "pickup_coin"
            self.amount = 100.0

    def get_hitbox(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )

    def update(self, dt: float, player_x: float, player_y: float, magnet_active: bool):
        """Handle magnet pull towards player vehicle."""
        if magnet_active and not self.is_collected:
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.hypot(dx, dy)
            if dist < 170.0 and dist > 1.0:
                pull_speed = 340.0 * (1.0 - (dist / 170.0) * 0.4)
                self.x += (dx / dist) * pull_speed * dt
                self.y += (dy / dist) * pull_speed * dt

    def render(self, surface: pygame.Surface, camera, asset_pipeline):
        if self.is_collected:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sy < -40 or sy > camera.height + 40:
            return

        # Bobbing floating motion
        bob = int(math.sin(pygame.time.get_ticks() * 0.008 + self.x) * 3)
        sprite = asset_pipeline.get_surface(self.sprite_name, pygame)
        if sprite:
            surface.blit(sprite, (sx - self.width // 2, sy - self.height // 2 + bob))
        else:
            pygame.draw.circle(surface, COLOR_YELLOW, (sx, sy + bob), 12)


class Hazard:
    """Road hazard causing spin-outs or minor damage."""

    def __init__(self, x: float, y: float, hazard_type: HazardType):
        self.x = float(x)
        self.y = float(y)
        self.hazard_type = hazard_type
        self.is_hit = False

        if hazard_type == HazardType.OIL_SLICK:
            self.sprite_name = "hazard_oil"
            self.width = 42
            self.height = 28
        else:
            self.sprite_name = "hazard_cone"
            self.width = 24
            self.height = 24

    def get_hitbox(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )

    def render(self, surface: pygame.Surface, camera, asset_pipeline):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sy < -40 or sy > camera.height + 40:
            return
        sprite = asset_pipeline.get_surface(self.sprite_name, pygame)
        if sprite:
            surface.blit(sprite, (sx - self.width // 2, sy - self.height // 2))
        else:
            pygame.draw.circle(surface, (20, 20, 20), (sx, sy), 14)
