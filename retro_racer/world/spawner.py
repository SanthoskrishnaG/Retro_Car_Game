"""Dynamic Spawner for Traffic, Pickups, Hazards, and Roadside Scenery with Deterministic Seeding."""

import random
from typing import List, Tuple, Optional
import pygame

from retro_racer.entities.traffic import TrafficCar, EnemyBehavior
from retro_racer.entities.pickups import Pickup, PickupType, Hazard, HazardType
from retro_racer.entities.roadside import RoadsideObject
from retro_racer.world.road import RoadManager
from retro_racer.config import (
    ROAD_LANES, LANE_WIDTH, MAX_CONCURRENT_TRAFFIC,
    TRAFFIC_SPAWN_INTERVAL_MIN, TRAFFIC_SPAWN_INTERVAL_MAX
)


class WorldSpawner:
    """Manages spawning intervals and recycling of all world objects with deterministic seeding support."""

    def __init__(self, road_system: RoadManager, seed: Optional[int] = None):
        self.road_system = road_system
        self.seed = seed
        self.rng = random.Random(seed) if seed is not None else random.Random()

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

    def reset(self, start_y: float = 0.0, seed: Optional[int] = None):
        """Clear all active entities and optionally re-seed."""
        if seed is not None:
            self.seed = seed
            self.rng = random.Random(seed)

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
        # Dynamic difficulty scaling with distance
        difficulty = 1.0 + min(1.6, player_distance / 1500.0)

        # 1. Update Traffic Spawning
        self.traffic_timer -= dt * difficulty
        if self.traffic_timer <= 0:
            interval = self.rng.uniform(TRAFFIC_SPAWN_INTERVAL_MIN, TRAFFIC_SPAWN_INTERVAL_MAX) / difficulty
            self.traffic_timer = interval
            if len(self.traffic_cars) < MAX_CONCURRENT_TRAFFIC:
                self._spawn_traffic_car(player_y, difficulty)

        # 2. Update Pickup Spawning
        self.pickup_timer -= dt
        if self.pickup_timer <= 0:
            self.pickup_timer = self.rng.uniform(3.0, 5.0)
            self._spawn_pickup(player_y)

        # 3. Update Hazard Spawning
        self.hazard_timer -= dt
        if self.hazard_timer <= 0:
            self.hazard_timer = self.rng.uniform(4.0, 7.0)
            self._spawn_hazard(player_y)

        # 4. Continuous Roadside Scenery Generation ahead
        while self.scenery_spawn_y < player_y + 800.0:
            self._spawn_roadside_pair(self.scenery_spawn_y)
            self.scenery_spawn_y += self.rng.uniform(50.0, 100.0)

        # 5. Entity Culling
        despawn_behind_y = player_y - 300.0
        despawn_ahead_y = player_y + 1400.0

        self.traffic_cars = [c for c in self.traffic_cars if despawn_behind_y <= c.position_y <= despawn_ahead_y]
        self.pickups = [p for p in self.pickups if not p.is_collected and despawn_behind_y <= p.y <= despawn_ahead_y]
        self.hazards = [h for h in self.hazards if not h.is_hit and despawn_behind_y <= h.y <= despawn_ahead_y]
        self.roadside_objects = [r for r in self.roadside_objects if despawn_behind_y <= r.y <= despawn_ahead_y]

    def _spawn_traffic_car(self, player_y: float, difficulty: float):
        """Spawn an enemy traffic car ahead with behavior archetype selected by difficulty."""
        spawn_y = player_y + self.rng.uniform(400.0, 650.0)
        lane_idx = self.rng.randint(0, ROAD_LANES - 1)
        spawn_x = self.road_system.get_lane_center_x(lane_idx, spawn_y)

        # Behavior distribution scales with difficulty
        behaviors = [EnemyBehavior.NORMAL, EnemyBehavior.SLOW, EnemyBehavior.FAST]
        weights = [0.45, 0.35, 0.20]

        if difficulty > 1.2:
            behaviors.extend([EnemyBehavior.LANE_CHANGER, EnemyBehavior.OVERTAKER])
            weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        if difficulty > 1.5:
            behaviors.append(EnemyBehavior.AGGRESSIVE)
            weights = [0.25, 0.20, 0.20, 0.15, 0.10, 0.10]

        chosen_behavior = self.rng.choices(behaviors, weights=weights, k=1)[0]
        car_seed = self.rng.randint(0, 999999) if self.seed is not None else None
        car = TrafficCar(spawn_x, spawn_y, chosen_behavior, lane_idx=lane_idx, seed=car_seed)
        self.traffic_cars.append(car)

    def _spawn_pickup(self, player_y: float):
        """Spawn a fuel, nitro, coin, or powerup pickup item."""
        spawn_y = player_y + self.rng.uniform(450.0, 700.0)
        lane_idx = self.rng.randint(0, ROAD_LANES - 1)
        spawn_x = self.road_system.get_lane_center_x(lane_idx, spawn_y)

        pickup_types = [
            PickupType.COIN, PickupType.FUEL, PickupType.NITRO,
            PickupType.SHIELD, PickupType.MAGNET, PickupType.SLOWMO,
            PickupType.MULTIPLIER_2X, PickupType.WRENCH
        ]
        weights = [0.38, 0.22, 0.16, 0.05, 0.05, 0.05, 0.05, 0.04]
        ptype = self.rng.choices(pickup_types, weights=weights, k=1)[0]

        self.pickups.append(Pickup(spawn_x, spawn_y, ptype))

    def _spawn_hazard(self, player_y: float):
        """Spawn an oil slick or cone hazard."""
        spawn_y = player_y + self.rng.uniform(500.0, 750.0)
        lane_idx = self.rng.randint(0, ROAD_LANES - 1)
        spawn_x = self.road_system.get_lane_center_x(lane_idx, spawn_y)
        htype = self.rng.choice([HazardType.OIL_SLICK, HazardType.ROAD_CONE])
        self.hazards.append(Hazard(spawn_x, spawn_y, htype))

    def _spawn_roadside_pair(self, y: float):
        """Place scenery decorations along the left and right verges."""
        seg = self.road_system.get_segment_at(y)
        _, left_edge, right_edge = self.road_system.get_road_bounds(y)

        # Left Scenery
        left_sprite = seg.scenery_left
        left_x = left_edge - self.rng.uniform(22.0, 48.0)
        self.roadside_objects.append(RoadsideObject(left_x, y, left_sprite, side="left"))

        # Right Scenery
        right_sprite = seg.scenery_right
        right_x = right_edge + self.rng.uniform(22.0, 48.0)
        self.roadside_objects.append(RoadsideObject(right_x, y, right_sprite, side="right"))
