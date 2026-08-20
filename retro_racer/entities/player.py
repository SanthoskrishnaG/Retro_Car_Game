"""Player Vehicle Controller with Nitro, Fuel, Upgrades, and Power-Up status."""

import math
from typing import Dict, Any, Optional
import pygame

from retro_racer.entities.car import BaseCar
from retro_racer.config import (
    PLAYER_BASE_MAX_SPEED, PLAYER_ACCELERATION, PLAYER_BRAKING_FORCE,
    PLAYER_FRICTION, PLAYER_STEERING_SPEED, PLAYER_DRIFT_FACTOR,
    PLAYER_OFFROAD_DECEL, PLAYER_OFFROAD_MAX_SPEED,
    NITRO_MAX, NITRO_DEPLETION_RATE, NITRO_SPEED_MULTIPLIER, NITRO_RECHARGE_RATE,
    FUEL_MAX, FUEL_DEPLETION_BASE, FUEL_DEPLETION_SPEED_SCALE,
    SHIELD_DURATION, MAGNET_DURATION, SLOW_MO_DURATION, DOUBLE_SCORE_DURATION
)


class PlayerCar(BaseCar):
    """Player-controlled racing car with physics, nitro booster, fuel management, and power-ups."""

    def __init__(self, x: float, y: float, sprite_name: str = "player_red"):
        super().__init__(x, y, width=24, height=44, sprite_name=sprite_name)

        # Baseline vehicle model properties
        self.base_max_speed = PLAYER_BASE_MAX_SPEED
        self.max_speed = self.base_max_speed
        self.acceleration = PLAYER_ACCELERATION
        self.braking_force = PLAYER_BRAKING_FORCE
        self.friction = PLAYER_FRICTION
        self.steering_speed = PLAYER_STEERING_SPEED
        self.drift_factor = PLAYER_DRIFT_FACTOR
        self.fuel_efficiency = 1.0

        # Fuel & Nitro Gauges
        self.fuel = FUEL_MAX
        self.nitro = 60.0
        self.is_nitro_active = False
        self.out_of_fuel_timer = 0.0

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
        self.cleared_checkpoints = set()

        # Visuals & Input State
        self.is_braking = False

    def apply_upgrades(self, upgrades: Dict[str, int]):
        """Apply career garage upgrade levels (0 to 5) to vehicle performance."""
        lvl_speed = upgrades.get("upgrade_top_speed", 0)
        lvl_accel = upgrades.get("upgrade_accel", 0)
        lvl_handling = upgrades.get("upgrade_handling", 0)
        lvl_nitro = upgrades.get("upgrade_nitro", 0)
        lvl_fuel = upgrades.get("upgrade_fuel_efficiency", 0)

        self.max_speed = self.base_max_speed + (lvl_speed * 25.0)
        self.acceleration = PLAYER_ACCELERATION + (lvl_accel * 30.0)
        self.steering_speed = PLAYER_STEERING_SPEED + (lvl_handling * 20.0)
        self.fuel_efficiency = 1.0 + (lvl_fuel * 0.18)

    def update_physics(self, dt: float, steer_input: float, throttle: bool, brake: bool, nitro_req: bool,
                       road_left: float, road_right: float, particle_system=None, audio_mgr=None):
        """Update vehicle dynamics, friction, drift, and forward motion using delta time."""
        # 1. Crash State Handling
        if self.is_crashed:
            self.speed = max(0.0, self.speed - self.braking_force * 1.5 * dt)
            self.velocity_y = self.speed
            self.position_y += self.velocity_y * dt
            self.position_x += self.velocity_x * dt
            self.velocity_x *= max(0.0, 1.0 - 5.0 * dt)
            self.update_spin(dt)
            if particle_system and self.speed > 20.0:
                particle_system.spawn_smoke(self.position_x, self.position_y)
            return

        self.is_braking = brake

        # 2. Check Out of Fuel State
        has_fuel = self.fuel > 0.0
        if not has_fuel:
            throttle = False
            nitro_req = False
            self.out_of_fuel_timer += dt
            if particle_system and random_condition(dt * 8) and self.speed > 10.0:
                particle_system.spawn_smoke(self.position_x, self.position_y + self.height // 2)

        # 3. Check offroad status
        offroad = self.is_offroad(road_left, road_right)

        # 4. Nitro Boost Logic
        self.is_nitro_active = nitro_req and has_fuel and (self.nitro > 2.0) and (self.speed > 60.0) and not offroad
        if self.is_nitro_active:
            self.nitro = max(0.0, self.nitro - NITRO_DEPLETION_RATE * dt)
            # Nitro score bonus
            self.score += int(10 * dt * (2 if self.double_score_timer > 0 else 1))
            if audio_mgr and random_condition(dt):
                audio_mgr.play_sfx("nitro", volume_scale=0.3)
        else:
            self.nitro = min(NITRO_MAX, self.nitro + NITRO_RECHARGE_RATE * dt)

        # 5. Calculate Speed Limits & Accel Rates
        curr_max_speed = self.max_speed * (NITRO_SPEED_MULTIPLIER if self.is_nitro_active else 1.0)
        curr_accel = self.acceleration * (1.6 if self.is_nitro_active else 1.0)

        if offroad:
            curr_max_speed = min(curr_max_speed, PLAYER_OFFROAD_MAX_SPEED)

        # 6. Acceleration & Braking with Delta Time
        if throttle or self.is_nitro_active:
            if self.speed < curr_max_speed:
                self.speed = min(curr_max_speed, self.speed + curr_accel * dt)
            elif self.speed > curr_max_speed:
                self.speed = max(curr_max_speed, self.speed - self.friction * dt)
        elif brake:
            self.speed = max(0.0, self.speed - self.braking_force * dt)
            if self.speed > 80.0 and particle_system:
                particle_system.spawn_skid(self.position_x - 8, self.position_y)
                particle_system.spawn_skid(self.position_x + 8, self.position_y)
        else:
            # Natural coasting friction (stronger deceleration when out of fuel)
            friction_rate = self.friction * (1.8 if not has_fuel else 1.0)
            self.speed = max(0.0, self.speed - friction_rate * dt)

        # Offroad extra deceleration penalty
        if offroad and self.speed > PLAYER_OFFROAD_MAX_SPEED:
            self.speed = max(PLAYER_OFFROAD_MAX_SPEED, self.speed - PLAYER_OFFROAD_DECEL * dt)

        # 7. Steering & Lateral Velocity Integration
        target_lateral_vel = steer_input * self.steering_speed
        smooth_rate = min(1.0, 10.0 * dt)
        self.velocity_x = (self.velocity_x * (1.0 - smooth_rate)) + (target_lateral_vel * smooth_rate)

        speed_factor = min(1.0, self.speed / 60.0)
        self.position_x += self.velocity_x * speed_factor * dt

        # Forward velocity
        self.velocity_y = self.speed
        self.position_y += self.velocity_y * dt

        # Distance & Speed Score Progression
        meters_delta = (self.speed * dt) / 50.0
        self.distance += meters_delta
        speed_bonus = int((self.speed / 80.0) * meters_delta * (2 if self.double_score_timer > 0 else 1))
        self.score += speed_bonus

        # 8. Fuel Consumption
        if has_fuel and self.speed > 5.0:
            fuel_loss = (FUEL_DEPLETION_BASE + (self.speed * FUEL_DEPLETION_SPEED_SCALE)) * (1.0 / self.fuel_efficiency) * dt
            self.fuel = max(0.0, self.fuel - fuel_loss)

        # 9. Update Power-Up Timers
        if self.shield_timer > 0:
            self.shield_timer = max(0.0, self.shield_timer - dt)
        if self.magnet_timer > 0:
            self.magnet_timer = max(0.0, self.magnet_timer - dt)
        if self.slowmo_timer > 0:
            self.slowmo_timer = max(0.0, self.slowmo_timer - dt)
        if self.double_score_timer > 0:
            self.double_score_timer = max(0.0, self.double_score_timer - dt)

        # 10. Update Combo Timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0

        # 11. Oil Spin Update
        self.update_spin(dt)

        # 12. Particle Emitters
        if particle_system:
            if self.is_nitro_active:
                particle_system.spawn_nitro_flame(self.position_x, self.position_y + self.height // 2)
            elif self.speed > 40.0 and random_condition(dt * 15):
                particle_system.spawn_smoke(self.position_x - 6, self.position_y + self.height // 2)

    def trigger_near_miss(self, base_score: int = 250) -> int:
        """Trigger near miss combo reward (+250 base)."""
        self.combo_count += 1
        self.combo_timer = 2.5
        self.nitro = min(NITRO_MAX, self.nitro + 12.0)
        mult = 2 if self.double_score_timer > 0 else 1
        pts = (base_score + (self.combo_count - 1) * 60) * mult
        self.score += pts
        return pts

    def trigger_overtake(self, base_score: int = 100) -> int:
        """Trigger clean overtake reward (+100 base)."""
        self.combo_count += 1
        self.combo_timer = 2.5
        mult = 2 if self.double_score_timer > 0 else 1
        pts = (base_score + (self.combo_count - 1) * 25) * mult
        self.score += pts
        return pts

    def trigger_checkpoint(self, checkpoint_id: int, base_score: int = 1000) -> int:
        """Trigger checkpoint time & score reward (+1000 base)."""
        self.cleared_checkpoints.add(checkpoint_id)
        # Bonus fuel on checkpoint
        self.fuel = min(FUEL_MAX, self.fuel + 25.0)
        mult = 2 if self.double_score_timer > 0 else 1
        pts = base_score * mult
        self.score += pts
        return pts

    def render_powerup_auras(self, surface: pygame.Surface, camera):
        """Render glowing energy aura when shield or magnet is active."""
        sx, sy = camera.world_to_screen(self.position_x, self.position_y)
        if self.shield_timer > 0:
            aura_radius = int(self.height * 0.65)
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 3
            pygame.draw.circle(surface, (0, 230, 255, 120), (sx, sy), int(aura_radius + pulse), width=2)
            pygame.draw.circle(surface, (180, 250, 255, 80), (sx, sy), int(aura_radius + pulse - 3), width=1)
        if self.magnet_timer > 0:
            mag_radius = int(self.height * 0.85)
            wave = (pygame.time.get_ticks() % 1000) / 1000.0
            pygame.draw.circle(surface, (255, 215, 0, int(150 * (1 - wave))), (sx, sy), int(mag_radius * wave), width=1)


def random_condition(rate: float) -> bool:
    import random
    return random.random() < rate
