"""Enemy Traffic AI with multiple vehicle archetypes, behaviors, and deterministic seeding."""

import random
import math
from enum import Enum
from typing import List, Optional, Tuple
import pygame

from retro_racer.entities.car import BaseCar
from retro_racer.config import (
    LANE_WIDTH, ROAD_LEFT_EDGE, ROAD_RIGHT_EDGE, ROAD_LANES,
    MIN_TRAFFIC_SPEED, MAX_TRAFFIC_SPEED
)


class EnemyBehavior(Enum):
    NORMAL = "normal"
    SLOW = "slow"
    FAST = "fast"
    AGGRESSIVE = "aggressive"
    LANE_CHANGER = "lane_changer"
    OVERTAKER = "overtaker"


# Backward compatibility alias
TrafficType = EnemyBehavior


class TrafficCar(BaseCar):
    """Enemy traffic car with distinctive AI behaviors and deterministic support."""

    def __init__(self, x: float, y: float, behavior: EnemyBehavior = EnemyBehavior.NORMAL,
                 lane_idx: int = 1, seed: Optional[int] = None):
        # Deterministic generator if seed provided
        self.rng = random.Random(seed) if seed is not None else random.Random()

        self.behavior: EnemyBehavior = behavior
        self.lane: int = lane_idx
        self.target_lane_x: float = float(x)
        self.lane_change_timer: float = self.rng.uniform(3.0, 7.0)
        self.turn_signal_timer: float = 0.0
        self.is_signaling_left: bool = False
        self.is_signaling_right: bool = False
        self.siren_timer: float = 0.0

        # Archetype setup
        if behavior == EnemyBehavior.SLOW:
            sprite = self.rng.choice(["traffic_truck_red", "traffic_truck_blue"])
            width, height = 30, 75
            speed = self.rng.uniform(110.0, 150.0)
            health = 160.0
        elif behavior == EnemyBehavior.FAST:
            sprite = self.rng.choice(["traffic_sport_pink", "traffic_sport_orange"])
            width, height = 24, 44
            speed = self.rng.uniform(250.0, 310.0)
            health = 80.0
        elif behavior == EnemyBehavior.AGGRESSIVE:
            sprite = "traffic_police"
            width, height = 24, 44
            speed = self.rng.uniform(210.0, 260.0)
            health = 120.0
        elif behavior == EnemyBehavior.OVERTAKER:
            sprite = self.rng.choice(["traffic_sport_orange", "traffic_sedan_blue"])
            width, height = 24, 44
            speed = self.rng.uniform(230.0, 280.0)
            health = 90.0
        elif behavior == EnemyBehavior.LANE_CHANGER:
            sprite = "traffic_taxi"
            width, height = 24, 44
            speed = self.rng.uniform(170.0, 220.0)
            health = 100.0
        else:  # NORMAL
            sprite = self.rng.choice(["traffic_sedan_blue", "traffic_sedan_white"])
            width, height = 24, 44
            speed = self.rng.uniform(160.0, 210.0)
            health = 100.0

        super().__init__(x, y, width=width, height=height, sprite_name=sprite)
        self.speed = speed
        self.desired_speed = speed
        self.health = health
        self.max_health = health

    @property
    def sprite(self) -> str:
        return self.sprite_name

    @property
    def position(self) -> Tuple[float, float]:
        return (self.position_x, self.position_y)

    def update_ai(self, dt: float, all_traffic: List["TrafficCar"], player=None,
                  road_lanes: int = ROAD_LANES, road_left: float = ROAD_LEFT_EDGE, road_right: float = ROAD_RIGHT_EDGE):
        """Update traffic AI decision making, lane following, and collision avoidance."""
        if self.is_crashed:
            self.speed = max(0.0, self.speed - 300.0 * dt)
            self.velocity_y = self.speed
            self.position_y += self.velocity_y * dt
            self.position_x += self.velocity_x * dt
            self.velocity_x *= max(0.0, 1.0 - 4.0 * dt)
            self.update_spin(dt)
            return

        # 1. Lookahead Ray: Detect cars ahead in same lane
        dist_ahead = 90.0 if self.behavior in (EnemyBehavior.FAST, EnemyBehavior.OVERTAKER) else 65.0
        car_ahead = None
        min_gap = 9999.0

        for other in all_traffic:
            if other is self:
                continue
            if abs(other.position_x - self.position_x) < 26.0 and (other.position_y > self.position_y) and ((other.position_y - self.position_y) < dist_ahead):
                gap = other.position_y - self.position_y
                if gap < min_gap:
                    min_gap = gap
                    car_ahead = other

        # 2. Behavior Actions
        if car_ahead:
            # Brake to avoid rear-ending
            self.speed = max(90.0, min(self.speed, car_ahead.speed - 10.0))

            # If overtaker or fast vehicle, initiate lane change to pass
            if self.behavior in (EnemyBehavior.OVERTAKER, EnemyBehavior.FAST, EnemyBehavior.AGGRESSIVE):
                self._trigger_overtake(all_traffic, road_lanes, road_left)
        else:
            # Accelerate smoothly back to desired cruise speed
            if self.speed < self.desired_speed:
                self.speed = min(self.desired_speed, self.speed + 120.0 * dt)

        # 3. Aggressive behavior: react to player proximity
        if self.behavior == EnemyBehavior.AGGRESSIVE and player and not player.is_crashed:
            dy = player.position_y - self.position_y
            if -120.0 < dy < 150.0:
                # Steer towards player's lane to block/intercept
                target_x = player.position_x
                if abs(target_x - self.position_x) > 10.0:
                    self.target_lane_x += (1.0 if target_x > self.position_x else -1.0) * 45.0 * dt

        # 4. Lane Changer behavior: periodic lane shifts
        if self.behavior == EnemyBehavior.LANE_CHANGER:
            self.lane_change_timer -= dt
            if self.lane_change_timer <= 0:
                self.lane_change_timer = self.rng.uniform(4.0, 8.0)
                shift = self.rng.choice([-1, 1])
                new_lane = max(0, min(road_lanes - 1, self.lane + shift))
                if new_lane != self.lane:
                    self.lane = new_lane
                    lane_w = (road_right - road_left) / road_lanes
                    self.target_lane_x = road_left + (self.lane * lane_w) + lane_w / 2

        # 5. Smooth steering towards target lane center
        lateral_error = self.target_lane_x - self.position_x
        self.velocity_x = lateral_error * 3.5
        self.position_x += self.velocity_x * dt

        # Forward velocity
        self.velocity_y = self.speed
        self.position_y += self.velocity_y * dt

        # Flashing police siren timer
        if self.behavior == EnemyBehavior.AGGRESSIVE:
            self.siren_timer += dt

    def _trigger_overtake(self, all_traffic: List["TrafficCar"], road_lanes: int, road_left: float):
        """Find an adjacent open lane with no cars blocking."""
        lane_w = LANE_WIDTH
        for shift in [-1, 1, 2, -2]:
            candidate = self.lane + shift
            if 0 <= candidate < road_lanes:
                cand_x = road_left + (candidate * lane_w) + lane_w / 2
                # Check if clear
                is_clear = True
                for other in all_traffic:
                    if other is not self and abs(other.position_x - cand_x) < 24.0:
                        if abs(other.position_y - self.position_y) < 70.0:
                            is_clear = False
                            break
                if is_clear:
                    self.lane = candidate
                    self.target_lane_x = cand_x
                    break

    def render(self, surface: pygame.Surface, camera, asset_pipeline, is_braking: bool = False):
        super().render(surface, camera, asset_pipeline, is_braking=is_braking)

        # Flashing lights for aggressive police interceptor
        if self.behavior == EnemyBehavior.AGGRESSIVE:
            sx, sy = camera.world_to_screen(self.position_x, self.position_y)
            flash = int(self.siren_timer * 8) % 2 == 0
            glow_col = (255, 30, 30, 160) if flash else (30, 80, 255, 160)
            glow_surf = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, glow_col, (7, 7), 6)
            surface.blit(glow_surf, (sx - 7, sy - 7))
