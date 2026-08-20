"""Player Vehicle Controller with Nitro, Fuel, Upgrades, and Power-Up status."""

import math
from typing import Dict, Any, Optional
import pygame

from retro_racer.entities.car import BaseCar
from retro_racer.config import (
    PLAYER_BASE_MAX_SPEED, PLAYER_ACCELERATION, PLAYER_BRAKING,
    PLAYER_NATURAL_DECEL, PLAYER_STEER_SPEED, PLAYER_DRIFT_FACTOR,
    PLAYER_OFFROAD_DECEL, PLAYER_OFFROAD_MAX_SPEED,
    NITRO_MAX, NITRO_DEPLETION_RATE, NITRO_SPEED_MULTIPLIER, NITRO_RECHARGE_RATE,
    FUEL_MAX, FUEL_DEPLETION_BASE, FUEL_DEPLETION_SPEED_SCALE,
    SHIELD_DURATION, MAGNET_DURATION, SLOW_MO_DURATION, DOUBLE_SCORE_DURATION
)


class PlayerCar(BaseCar):
    """Player-controlled racing car with nitro booster, fuel management, and power-ups."""

    def __init__(self, x: float, y: float, sprite_name: str = "player_red"):
        super().__init__(x, y, width=34, height=62, sprite_name=sprite_name)

        # Baseline stats
        self.base_max_speed = PLAYER_BASE_MAX_SPEED
        self.base_accel = PLAYER_ACCELERATION
        self.base_steer = PLAYER_STEER_SPEED
        self.fuel_efficiency = 1.0

        # Fuel & Nitro Gauges
        self.fuel = FUEL_MAX
        self.nitro = 60.0
        self.is_nitro_active = False

        # Power-Up Active Timers
        self.shield_timer = 0.0
        self.magnet_timer = 0.0
        self.slowmo_timer = 0.0
        self.double_score_timer = 0.0

        # Combo & Scoring
        self.score = 0
        self.distance = 0.0
        self.combo_count = 0
        self.combo_timer = 0.0
        self.overtaken_cars = set()

        # Visuals
        self.is_braking = False

    def apply_upgrades(self, upgrades: Dict[str, int]):
        """Apply career garage upgrade levels (0 to 5) to vehicle performance."""
        lvl_speed = upgrades.get("upgrade_top_speed", 0)
        lvl_accel = upgrades.get("upgrade_accel", 0)
        lvl_handling = upgrades.get("upgrade_handling", 0)
        lvl_nitro = upgrades.get("upgrade_nitro", 0)
        lvl_fuel = upgrades.get("upgrade_fuel_efficiency", 0)

        self.max_speed = self.base_max_speed + (lvl_speed * 30.0)
        self.acceleration = self.base_accel + (lvl_accel * 35.0)
        self.steer_speed = self.base_steer + (lvl_handling * 25.0)
        self.fuel_efficiency = 1.0 + (lvl_fuel * 0.18)

    def update_physics(self, dt: float, steer_input: float, throttle: bool, brake: bool, nitro_req: bool,
                       road_left: float, road_right: float, particle_system=None, audio_mgr=None):
        """Update vehicle dynamics, friction, drift, and forward motion."""
        if self.is_crashed:
            self.speed = max(0.0, self.speed - PLAYER_BRAKING * 1.5 * dt)
            self.update_spin(dt)
            return

        self.is_braking = brake

        # Check offroad status
        offroad = self.is_offroad(road_left, road_right)

        # Nitro Activation Logic
        self.is_nitro_active = nitro_req and (self.nitro > 2.0) and (self.speed > 80.0) and not offroad
        if self.is_nitro_active:
            self.nitro = max(0.0, self.nitro - NITRO_DEPLETION_RATE * dt)
            if audio_mgr and random_condition(dt):
                audio_mgr.play_sfx("nitro", volume_scale=0.3)
        else:
            # Passive slow nitro trickle
            self.nitro = min(NITRO_MAX, self.nitro + NITRO_RECHARGE_RATE * dt)

        # Calculate Max Speed & Accel for this tick
        curr_max_speed = self.max_speed * (NITRO_SPEED_MULTIPLIER if self.is_nitro_active else 1.0)
        curr_accel = self.acceleration * (1.6 if self.is_nitro_active else 1.0)

        if offroad:
            curr_max_speed = min(curr_max_speed, PLAYER_OFFROAD_MAX_SPEED)

        # Acceleration / Deceleration
        if throttle or self.is_nitro_active:
            if self.speed < curr_max_speed:
                self.speed = min(curr_max_speed, self.speed + curr_accel * dt)
            elif self.speed > curr_max_speed:
                self.speed -= PLAYER_NATURAL_DECEL * dt
        elif brake:
            self.speed = max(0.0, self.speed - PLAYER_BRAKING * dt)
            if self.speed > 100.0 and particle_system:
                particle_system.spawn_skid(self.x - 10, self.y)
                particle_system.spawn_skid(self.x + 10, self.y)
        else:
            # Natural coasting drag
            self.speed = max(0.0, self.speed - PLAYER_NATURAL_DECEL * dt)

        if offroad and self.speed > PLAYER_OFFROAD_MAX_SPEED:
            self.speed = max(PLAYER_OFFROAD_MAX_SPEED, self.speed - PLAYER_OFFROAD_DECEL * dt)

        # Steering & Lateral Velocity
        target_lateral = steer_input * self.steer_speed
        self.lateral_speed = (self.lateral_speed * PLAYER_DRIFT_FACTOR) + (target_lateral * (1.0 - PLAYER_DRIFT_FACTOR))

        # Can only steer if car is moving forward
        speed_ratio = min(1.0, self.speed / 100.0)
        self.x += self.lateral_speed * speed_ratio * dt
        self.y += self.speed * dt
        self.distance += (self.speed * dt) / 50.0  # approximate meters

        # Fuel Consumption
        fuel_loss = (FUEL_DEPLETION_BASE + (self.speed * FUEL_DEPLETION_SPEED_SCALE)) * (1.0 / self.fuel_efficiency) * dt
        self.fuel = max(0.0, self.fuel - fuel_loss)

        # Update Power-Up timers
        if self.shield_timer > 0:
            self.shield_timer -= dt
        if self.magnet_timer > 0:
            self.magnet_timer -= dt
        if self.slowmo_timer > 0:
            self.slowmo_timer -= dt
        if self.double_score_timer > 0:
            self.double_score_timer -= dt

        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0

        # Oil Spin update
        self.update_spin(dt)

        # Particle Emitters (Exhaust smoke & Nitro jet fire)
        if particle_system:
            if self.is_nitro_active:
                particle_system.spawn_nitro_flame(self.x, self.y + self.height // 2)
            elif self.speed > 50.0 and random_condition(dt * 15):
                particle_system.spawn_smoke(self.x - 8, self.y + self.height // 2)

    def trigger_near_miss(self, base_score: int = 150) -> int:
        """Trigger near miss combo reward."""
        self.combo_count += 1
        self.combo_timer = 2.5
        # Reward nitro
        self.nitro = min(NITRO_MAX, self.nitro + 12.0)
        # Score calculation
        mult = 2 if self.double_score_timer > 0 else 1
        pts = (base_score + (self.combo_count - 1) * 50) * mult
        self.score += pts
        return pts

    def collect_pickup(self, pickup_type: str, amount: float = 0.0):
        """Handle power-up collection."""
        if pickup_type == "fuel":
            self.fuel = min(FUEL_MAX, self.fuel + amount)
        elif pickup_type == "nitro":
            self.nitro = min(NITRO_MAX, self.nitro + amount)
        elif pickup_type == "coin":
            mult = 2 if self.double_score_timer > 0 else 1
            self.score += int(amount * mult)
        elif pickup_type == "shield":
            self.shield_timer = SHIELD_DURATION
        elif pickup_type == "magnet":
            self.magnet_timer = MAGNET_DURATION
        elif pickup_type == "slowmo":
            self.slowmo_timer = SLOW_MO_DURATION
        elif pickup_type == "2x":
            self.double_score_timer = DOUBLE_SCORE_DURATION
        elif pickup_type == "wrench":
            self.health = min(self.max_health, self.health + amount)

    def render_powerup_auras(self, surface: pygame.Surface, camera):
        """Render glowing energy aura when shield or magnet is active."""
        sx, sy = camera.world_to_screen(self.x, self.y)
        if self.shield_timer > 0:
            aura_radius = int(self.height * 0.65)
            # Pulsing cyan shield
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 3
            pygame.draw.circle(surface, (0, 230, 255, 120), (sx, sy), int(aura_radius + pulse), width=2)
            pygame.draw.circle(surface, (180, 250, 255, 80), (sx, sy), int(aura_radius + pulse - 3), width=1)
        if self.magnet_timer > 0:
            # Magnetic field waves
            mag_radius = int(self.height * 0.85)
            wave = (pygame.time.get_ticks() % 1000) / 1000.0
            pygame.draw.circle(surface, (255, 215, 0, int(150 * (1 - wave))), (sx, sy), int(mag_radius * wave), width=1)


def random_condition(rate: float) -> bool:
    import random
    return random.random() < rate
