"""Dynamic Spawner for Traffic, Pickups, Hazards, and Roadside Scenery."""

import random
from typing import List, Tuple
import pygame

from retro_racer.entities.traffic import TrafficCar, TrafficType
from retro_racer.entities.pickups import Pickup, PickupType, Hazard, HazardType
from retro_racer.entities.roadside import RoadsideObject
from retro_racer.world.road import RoadSystem
from retro_racer.config import (
    ROAD_LANES, LANE_WIDTH, MAX_CONCURRENT_TRAFFIC,
    TRAFFIC_SPAWN_INTERVAL_MIN, TRAFFIC_SPAWN_INTERVAL_MAX
)


class WorldSpawner:
    """Manages spawning intervals and recycling of all world objects."""

    def __init__(self, road_system: RoadSystem):
        self.road_system = road_system

        # Active entity lists
        self.traffic_cars: List[TrafficCar] = []
        self.pickups: List[Pickup] = []
        self.hazards: List[Hazard] = []
        self.roadside_objects: List[RoadsideObject] = []

        # Timers
        self.traffic_timer = 1.0
        self.pickup_timer = 2.0
        self.hazard_timer = 4.0
        self.scenery_spawn_y = 0.0

    def reset(self, start_y: float = 0.0):
        """Clear all active entities."""
        self.traffic_cars.clear()
        self.pickups.clear()
        self.hazards.clear()
        self.roadside_objects.clear()
        self.traffic_timer = 1.0
        self.pickup_timer = 2.0
        self.hazard_timer = 4.0
        self.scenery_spawn_y = start_y

    def update(self, dt: float, player_y: float, player_distance: float):
        """Spawn new entities ahead of player and cull off-screen objects behind."""
        # Calculate dynamic difficulty multiplier based on distance traveled
        difficulty = 1.0 + min(1.5, player_distance / 2000.0)

        # 1. Update Traffic Spawning
        self.traffic_timer -= dt * difficulty
        if self.traffic_timer <= 0:
            interval = random.uniform(TRAFFIC_SPAWN_INTERVAL_MIN, TRAFFIC_SPAWN_INTERVAL_MAX) / difficulty
            self.traffic_timer = interval
            if len(self.traffic_cars) < MAX_CONCURRENT_TRAFFIC:
                self._spawn_traffic_car(player_y, difficulty)

        # 2. Update Pickup Spawning
        self.pickup_timer -= dt
        if self.pickup_timer <= 0:
            self.pickup_timer = random.uniform(3.0, 5.5)
            self._spawn_pickup(player_y)

        # 3. Update Hazard Spawning
        self.hazard_timer -= dt
        if self.hazard_timer <= 0:
            self.hazard_timer = random.uniform(4.5, 7.5)
            self._spawn_hazard(player_y)

        # 4. Continuous Roadside Scenery Generation ahead
        while self.scenery_spawn_y < player_y + 1200.0:
            self._spawn_roadside_pair(self.scenery_spawn_y)
            self.scenery_spawn_y += random.uniform(70.0, 140.0)

        # 5. Entity Culling (Remove objects that are far behind or collected)
        despawn_behind_y = player_y - 450.0
        despawn_ahead_y = player_y + 2000.0

        self.traffic_cars = [c for c in self.traffic_cars if despawn_behind_y <= c.y <= despawn_ahead_y]
        self.pickups = [p for p in self.pickups if not p.is_collected and despawn_behind_y <= p.y <= despawn_ahead_y]
        self.hazards = [h for h in self.hazards if not h.is_hit and despawn_behind_y <= h.y <= despawn_ahead_y]
        self.roadside_objects = [r for r in self.roadside_objects if despawn_behind_y <= r.y <= despawn_ahead_y]

    def _spawn_traffic_car(self, player_y: float, difficulty: float):
        """Spawn a traffic vehicle in an available lane ahead or behind."""
        spawn_y = player_y + random.uniform(650.0, 950.0)
        lane_idx = random.randint(0, ROAD_LANES - 1)
        spawn_x = self.road_system.get_lane_center_x(lane_idx, spawn_y)

        # Determine archetype by weights
        types = [TrafficType.SEDAN, TrafficType.TRUCK, TrafficType.SPORT, TrafficType.TAXI]
        weights = [0.4, 0.25, 0.2, 0.15]

        if difficulty > 1.3:
            types.extend([TrafficType.WEAVER, TrafficType.POLICE])
            weights = [0.25, 0.2, 0.2, 0.15, 0.1, 0.1]

        chosen_type = random.choices(types, weights=weights, k=1)[0]
        car = TrafficCar(spawn_x, spawn_y, chosen_type, lane_idx=lane_idx)
        self.traffic_cars.append(car)

    def _spawn_pickup(self, player_y: float):
        """Spawn a fuel, nitro, coin, or powerup pickup item."""
        spawn_y = player_y + random.uniform(700.0, 1000.0)
        lane_idx = random.randint(0, ROAD_LANES - 1)
        spawn_x = self.road_system.get_lane_center_x(lane_idx, spawn_y)

        # Pickups distribution
        pickup_types = [
            PickupType.COIN, PickupType.FUEL, PickupType.NITRO,
            PickupType.SHIELD, PickupType.MAGNET, PickupType.SLOWMO,
            PickupType.MULTIPLIER_2X, PickupType.WRENCH
        ]
        weights = [0.4, 0.2, 0.15, 0.05, 0.05, 0.05, 0.05, 0.05]
        ptype = random.choices(pickup_types, weights=weights, k=1)[0]

        self.pickups.append(Pickup(spawn_x, spawn_y, ptype))

    def _spawn_hazard(self, player_y: float):
        """Spawn an oil slick or cone hazard."""
        spawn_y = player_y + random.uniform(750.0, 1050.0)
        lane_idx = random.randint(0, ROAD_LANES - 1)
        spawn_x = self.road_system.get_lane_center_x(lane_idx, spawn_y)
        htype = random.choice([HazardType.OIL_SLICK, HazardType.ROAD_CONE])
        self.hazards.append(Hazard(spawn_x, spawn_y, htype))

    def _spawn_roadside_pair(self, y: float):
        """Place scenery decorations along the left and right verges."""
        seg = self.road_system.get_segment_at(y)
        _, left_edge, right_edge = self.road_system.get_road_bounds(y)

        # Left Scenery
        left_sprite = seg.scenery_left
        left_x = left_edge - random.uniform(35.0, 75.0)
        self.roadside_objects.append(RoadsideObject(left_x, y, left_sprite, side="left"))

        # Right Scenery
        right_sprite = seg.scenery_right
        right_x = right_edge + random.uniform(35.0, 75.0)
        self.roadside_objects.append(RoadsideObject(right_x, y, right_sprite, side="right"))
