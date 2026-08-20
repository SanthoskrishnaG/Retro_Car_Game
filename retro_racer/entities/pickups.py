"""Generic PowerUp base class and power-up collectibles."""

import math
from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Optional
import pygame

from retro_racer.config import (
    FUEL_PICKUP_AMOUNT, COIN_SCORE, COLOR_YELLOW, COLOR_CYAN, COLOR_GREEN,
    SHIELD_DURATION, MAGNET_DURATION, SLOW_MO_DURATION, DOUBLE_SCORE_DURATION
)


class PickupType(Enum):
    FUEL = "fuel"
    NITRO = "nitro"
    COIN = "coin"
    SHIELD = "shield"
    MAGNET = "magnet"
    SLOWMO = "slowmo"
    MULTIPLIER_2X = "2x"
    REPAIR = "repair"
    WRENCH = "repair"


class HazardType(Enum):
    OIL_SLICK = "oil"
    ROAD_CONE = "cone"


class PowerUp(ABC):
    """Generic base class for all power-ups and collectibles."""

    def __init__(self, x: float, y: float, sprite_name: str, width: int = 20, height: int = 20):
        self.x: float = float(x)
        self.y: float = float(y)
        self.sprite_name: str = sprite_name
        self.width: int = width
        self.height: int = height
        self.is_collected: bool = False

    def get_hitbox(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )

    def update(self, dt: float, player_x: float, player_y: float, magnet_active: bool):
        """Magnet attraction toward player vehicle."""
        if magnet_active and not self.is_collected:
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.hypot(dx, dy)
            if 1.0 < dist < 120.0:
                pull_speed = 280.0 * (1.0 - (dist / 120.0) * 0.4)
                self.x += (dx / dist) * pull_speed * dt
                self.y += (dy / dist) * pull_speed * dt

    @abstractmethod
    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        """Apply power-up effect to player. Returns (notification_text, sound_name, color)."""
        pass

    def render(self, surface: pygame.Surface, camera, asset_pipeline):
        if self.is_collected:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sy < -30 or sy > camera.height + 30:
            return

        bob = int(math.sin(pygame.time.get_ticks() * 0.008 + self.x) * 2)
        sprite = asset_pipeline.get_surface(self.sprite_name, pygame)
        if sprite:
            w, h = sprite.get_size()
            # Scale to retro icon size if needed
            scaled = pygame.transform.scale(sprite, (self.width, self.height))
            surface.blit(scaled, (sx - self.width // 2, sy - self.height // 2 + bob))
        else:
            pygame.draw.circle(surface, COLOR_YELLOW, (sx, sy + bob), self.width // 2)


# Specific PowerUp Implementations

class FuelPowerUp(PowerUp):
    """Restores fuel tank level."""
    def __init__(self, x: float, y: float, amount: float = FUEL_PICKUP_AMOUNT):
        super().__init__(x, y, sprite_name="pickup_fuel", width=18, height=18)
        self.amount = amount
        self.pickup_type = PickupType.FUEL

    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        from retro_racer.config import FUEL_MAX
        player.fuel = min(FUEL_MAX, player.fuel + self.amount)
        return ("+FUEL", "pickup", COLOR_GREEN)


class NitroPowerUp(PowerUp):
    """Refills nitro boost capacity."""
    def __init__(self, x: float, y: float, amount: float = 40.0):
        super().__init__(x, y, sprite_name="pickup_nitro", width=18, height=18)
        self.amount = amount
        self.pickup_type = PickupType.NITRO

    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        from retro_racer.config import NITRO_MAX
        player.nitro = min(NITRO_MAX, player.nitro + self.amount)
        return ("+NITRO", "pickup", COLOR_CYAN)


class CoinPowerUp(PowerUp):
    """Increases score."""
    def __init__(self, x: float, y: float, amount: int = COIN_SCORE):
        super().__init__(x, y, sprite_name="pickup_coin", width=16, height=16)
        self.amount = amount
        self.pickup_type = PickupType.COIN

    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        mult = 2 if player.double_score_timer > 0 else 1
        pts = int(self.amount * mult)
        player.score += pts
        return (f"+{pts} PTS", "coin", COLOR_YELLOW)


class ShieldPowerUp(PowerUp):
    """Protects against one collision with forcefield."""
    def __init__(self, x: float, y: float, duration: float = SHIELD_DURATION):
        super().__init__(x, y, sprite_name="pickup_shield", width=18, height=18)
        self.duration = duration
        self.pickup_type = PickupType.SHIELD

    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        player.shield_timer = self.duration
        return ("SHIELD ON!", "pickup", COLOR_CYAN)


class RepairPowerUp(PowerUp):
    """Restores chassis health."""
    def __init__(self, x: float, y: float, amount: float = 35.0):
        super().__init__(x, y, sprite_name="pickup_wrench", width=18, height=18)
        self.amount = amount
        self.pickup_type = PickupType.REPAIR

    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        player.health = min(player.max_health, player.health + self.amount)
        return ("+REPAIR", "pickup", COLOR_GREEN)


class MagnetPowerUp(PowerUp):
    """Attracts pickups within range."""
    def __init__(self, x: float, y: float, duration: float = MAGNET_DURATION):
        super().__init__(x, y, sprite_name="pickup_magnet", width=18, height=18)
        self.duration = duration
        self.pickup_type = PickupType.MAGNET

    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        player.magnet_timer = self.duration
        return ("MAGNET ON!", "pickup", COLOR_YELLOW)


class SlowMoPowerUp(PowerUp):
    """Triggers bullet-time world slow motion."""
    def __init__(self, x: float, y: float, duration: float = SLOW_MO_DURATION):
        super().__init__(x, y, sprite_name="pickup_slowmo", width=18, height=18)
        self.duration = duration
        self.pickup_type = PickupType.SLOWMO

    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        player.slowmo_timer = self.duration
        return ("SLOW-MO!", "pickup", COLOR_CYAN)


class MultiplierPowerUp(PowerUp):
    """Doubles score gains."""
    def __init__(self, x: float, y: float, duration: float = DOUBLE_SCORE_DURATION):
        super().__init__(x, y, sprite_name="pickup_2x", width=18, height=18)
        self.duration = duration
        self.pickup_type = PickupType.MULTIPLIER_2X

    def apply(self, player) -> Tuple[str, str, Tuple[int, int, int]]:
        player.double_score_timer = self.duration
        return ("2X BONUS!", "pickup", COLOR_YELLOW)


def create_powerup(pickup_type: PickupType, x: float, y: float) -> PowerUp:
    """Factory helper creating concrete power-up instances."""
    if pickup_type == PickupType.FUEL:
        return FuelPowerUp(x, y)
    elif pickup_type == PickupType.NITRO:
        return NitroPowerUp(x, y)
    elif pickup_type == PickupType.COIN:
        return CoinPowerUp(x, y)
    elif pickup_type == PickupType.SHIELD:
        return ShieldPowerUp(x, y)
    elif pickup_type == PickupType.REPAIR or pickup_type == PickupType.WRENCH:
        return RepairPowerUp(x, y)
    elif pickup_type == PickupType.MAGNET:
        return MagnetPowerUp(x, y)
    elif pickup_type == PickupType.SLOWMO:
        return SlowMoPowerUp(x, y)
    elif pickup_type == PickupType.MULTIPLIER_2X:
        return MultiplierPowerUp(x, y)
    return CoinPowerUp(x, y)


# Compatibility Alias
Pickup = PowerUp


class Hazard:
    """Road hazard causing spin-outs or minor damage."""

    def __init__(self, x: float, y: float, hazard_type: HazardType):
        self.x = float(x)
        self.y = float(y)
        self.hazard_type = hazard_type
        self.is_hit = False

        if hazard_type == HazardType.OIL_SLICK:
            self.sprite_name = "hazard_oil"
            self.width = 28
            self.height = 18
        else:
            self.sprite_name = "hazard_cone"
            self.width = 16
            self.height = 16

    def get_hitbox(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )

    def render(self, surface: pygame.Surface, camera, asset_pipeline):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sy < -30 or sy > camera.height + 30:
            return
        sprite = asset_pipeline.get_surface(self.sprite_name, pygame)
        if sprite:
            scaled = pygame.transform.scale(sprite, (self.width, self.height))
            surface.blit(scaled, (sx - self.width // 2, sy - self.height // 2))
        else:
            pygame.draw.circle(surface, (20, 20, 20), (sx, sy), 10)
