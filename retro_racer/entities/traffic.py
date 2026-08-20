"""Traffic AI vehicles with distinctive driving behaviors and collision avoidance."""

import random
import math
from enum import Enum
from typing import List, Optional
import pygame

from retro_racer.entities.car import BaseCar
from retro_racer.config import (
    LANE_WIDTH, ROAD_LEFT_EDGE, ROAD_RIGHT_EDGE,
    MIN_TRAFFIC_SPEED, MAX_TRAFFIC_SPEED
)


class TrafficType(Enum):
    SEDAN = "sedan"
    SPORT = "sport"
    TRUCK = "truck"
    TAXI = "taxi"
    POLICE = "police"
    WEAVER = "weaver"


class TrafficCar(BaseCar):
    """AI Traffic Vehicle controlled by autonomous behavior logic."""

    def __init__(self, x: float, y: float, traffic_type: TrafficType, lane_idx: int = 1):
        self.traffic_type = traffic_type
        self.lane_idx = lane_idx
        self.target_lane_x = x
        self.lane_change_timer = random.uniform(3.0, 7.0)
        self.siren_timer = 0.0

        # Type-specific attributes
        if traffic_type == TrafficType.TRUCK:
            sprite = random.choice(["traffic_truck_red", "traffic_truck_blue"])
            width, height = 42, 104
            speed = random.uniform(160.0, 220.0)
        elif traffic_type == TrafficType.SPORT:
            sprite = random.choice(["traffic_sport_pink", "traffic_sport_orange"])
            width, height = 34, 62
            speed = random.uniform(300.0, 360.0)
        elif traffic_type == TrafficType.POLICE:
            sprite = "traffic_police"
            width, height = 34, 62
            speed = random.uniform(270.0, 330.0)
        elif traffic_type == TrafficType.TAXI:
            sprite = "traffic_taxi"
            width, height = 34, 62
            speed = random.uniform(220.0, 270.0)
        elif traffic_type == TrafficType.WEAVER:
            sprite = random.choice(["traffic_sport_orange", "traffic_sedan_blue"])
            width, height = 34, 62
            speed = random.uniform(240.0, 310.0)
        else:  # SEDAN
            sprite = random.choice(["traffic_sedan_blue", "traffic_sedan_white"])
            width, height = 34, 62
            speed = random.uniform(200.0, 260.0)

        super().__init__(x, y, width=width, height=height, sprite_name=sprite)
        self.speed = speed
        self.desired_speed = speed

    def update_ai(self, dt: float, all_traffic: List["TrafficCar"], road_lanes: int = 4, road_left: float = ROAD_LEFT_EDGE):
        """Update traffic AI decision making, lane following, and collision avoidance."""
        if self.is_crashed:
            self.speed = max(0.0, self.speed - 300.0 * dt)
            self.update_spin(dt)
            return

        # 1. Forward Raycast: Detect obstacles or slower cars ahead
        dist_ahead = 140.0 if self.traffic_type == TrafficType.SPORT else 100.0
        car_ahead = None
        min_gap = 9999.0

        for other in all_traffic:
            if other is self:
                continue
            # Same lane check (within 30px laterally)
            if abs(other.x - self.x) < 32.0 and (other.y > self.y) and ((other.y - self.y) < dist_ahead):
                gap = other.y - self.y
                if gap < min_gap:
                    min_gap = gap
                    car_ahead = other

        if car_ahead:
            # Match speed or slow down to prevent rear-ending
            self.speed = max(120.0, min(self.speed, car_ahead.speed - 15.0))
            # If sport or weaver, trigger lane change
            if self.traffic_type in (TrafficType.SPORT, TrafficType.WEAVER, TrafficType.POLICE):
                self.lane_change_timer = 0.0
        else:
            # Accelerate smoothly back to desired speed
            if self.speed < self.desired_speed:
                self.speed = min(self.desired_speed, self.speed + 100.0 * dt)

        # 2. Lane changing logic for aggressive/weaver cars
        self.lane_change_timer -= dt
        if self.lane_change_timer <= 0:
            self.lane_change_timer = random.uniform(4.0, 9.0)
            if self.traffic_type in (TrafficType.SPORT, TrafficType.WEAVER, TrafficType.TAXI):
                # Pick adjacent lane
                shift = random.choice([-1, 1])
                new_lane = max(0, min(road_lanes - 1, self.lane_idx + shift))
                if new_lane != self.lane_idx:
                    self.lane_idx = new_lane
                    self.target_lane_x = road_left + (self.lane_idx * LANE_WIDTH) + LANE_WIDTH / 2

        # 3. Smooth steering toward target lane center
        lateral_error = self.target_lane_x - self.x
        self.lateral_speed = lateral_error * 3.5
        self.x += self.lateral_speed * dt
        self.y += self.speed * dt

        # 4. Police Siren animation
        if self.traffic_type == TrafficType.POLICE:
            self.siren_timer += dt

    def render(self, surface: pygame.Surface, camera, asset_pipeline, is_braking: bool = False):
        """Draw traffic car and siren flashing if police."""
        super().render(surface, camera, asset_pipeline, is_braking=is_braking)

        # Flashing police lights
        if self.traffic_type == TrafficType.POLICE:
            sx, sy = camera.world_to_screen(self.x, self.y)
            flash = int(self.siren_timer * 8) % 2 == 0
            glow_col = (255, 30, 30, 160) if flash else (30, 80, 255, 160)
            glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, glow_col, (10, 10), 8)
            surface.blit(glow_surf, (sx - 10, sy - 10))
