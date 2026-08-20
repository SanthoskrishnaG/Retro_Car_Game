"""Dedicated RoadManager Engine for Curves, Lanes, Boundaries, and Scrolling Segments."""

import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
import pygame

from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, ROAD_LANES, LANE_WIDTH, ROAD_WIDTH,
    ROAD_CENTER_X, ROAD_LEFT_EDGE, ROAD_RIGHT_EDGE, STRIPE_LENGTH, STRIPE_GAP,
    CURB_WIDTH, COLOR_ASPHALT, COLOR_ROAD_EDGE, COLOR_WHITE, COLOR_YELLOW,
    COLOR_RED, BIOME_CITY
)
from retro_racer.systems.level_editor import TrackData, TrackSegment


@dataclass
class RoadSegment:
    """Represents a discrete continuous road segment."""
    start_y: float
    end_y: float
    width: int
    curve: float
    lanes: int
    environment: str
    scenery_left: str = "scenery_oak_tree"
    scenery_right: str = "scenery_street_lamp"

    @property
    def length(self) -> float:
        return self.end_y - self.start_y

    # Aliases
    @property
    def road_width(self) -> int:
        return self.width

    @property
    def biome(self) -> str:
        return self.environment


# Backward compatibility alias
RoadSegmentGeometry = RoadSegment


class RoadManager:
    """Road Engine managing position, width, lanes, markings, curves, scrolling, boundaries, and segments."""

    def __init__(self, track_data: Optional[TrackData] = None):
        self.segments: List[RoadSegment] = []
        self.total_length: float = 10000.0
        self.track_name: str = "Default Track"
        self.biome: str = BIOME_CITY
        self.road_center_base = float(ROAD_CENTER_X)

        # Weather particles (for RAIN biome)
        self.rain_drops: List[List[float]] = []
        self._init_rain()

        if track_data:
            self.load_track(track_data)
        else:
            self._generate_default_geometry()

    def _init_rain(self):
        self.rain_drops.clear()
        for _ in range(40):
            self.rain_drops.append([
                random.uniform(0, VIRTUAL_WIDTH),
                random.uniform(0, VIRTUAL_HEIGHT),
                random.uniform(400, 700),  # speed
                random.uniform(8, 16)      # length
            ])

    def load_track(self, track: TrackData):
        """Build continuous geometric segments from TrackData."""
        self.track_name = track.name
        self.biome = track.biome
        self.segments.clear()

        curr_y = 0.0
        for seg in track.segments:
            road_w = getattr(seg, "road_width", ROAD_WIDTH)
            num_lanes = getattr(seg, "lanes", ROAD_LANES)
            env = getattr(seg, "biome", BIOME_CITY)
            geom = RoadSegment(
                start_y=curr_y,
                end_y=curr_y + seg.length,
                width=road_w,
                curve=seg.curve,
                lanes=num_lanes,
                environment=env,
                scenery_left=getattr(seg, "scenery_left", "scenery_oak_tree"),
                scenery_right=getattr(seg, "scenery_right", "scenery_street_lamp")
            )
            self.segments.append(geom)
            curr_y += seg.length

        self.total_length = max(1000.0, curr_y)

    def _generate_default_geometry(self):
        """Fallback default multi-biome circuit."""
        self.segments = [
            RoadSegment(0.0, 1500.0, ROAD_WIDTH, 0.0, 4, BIOME_CITY, "scenery_oak_tree", "scenery_street_lamp"),
            RoadSegment(1500.0, 3000.0, ROAD_WIDTH, 0.35, 4, "countryside", "scenery_palm_tree", "scenery_billboard_retro"),
            RoadSegment(3000.0, 4500.0, ROAD_WIDTH, -0.4, 4, "desert", "scenery_cactus", "scenery_rock"),
            RoadSegment(4500.0, 6000.0, ROAD_WIDTH, 0.0, 4, "mountain", "scenery_pine_tree", "scenery_grandstand"),
        ]
        self.total_length = 6000.0

    def get_segment_at(self, y: float) -> RoadSegment:
        """Find segment at given world distance y (with looping)."""
        wrapped_y = y % self.total_length
        for seg in self.segments:
            if seg.start_y <= wrapped_y <= seg.end_y:
                return seg
        return self.segments[0]

    def get_curvature_at(self, y: float) -> float:
        """Interpolate smooth road curvature at distance y."""
        seg = self.get_segment_at(y)
        return seg.curve

    def get_road_bounds(self, y: float) -> Tuple[float, float, float]:
        """Get (center_x, left_edge, right_edge) at world_y."""
        seg = self.get_segment_at(y)
        half_w = seg.width / 2.0
        # Lateral offset from curve integration
        curve_offset = seg.curve * 16.0
        center_x = self.road_center_base + curve_offset
        return center_x, center_x - half_w, center_x + half_w

    def get_lane_center_x(self, lane_idx: int, y: float) -> float:
        """Get lateral center coordinate for a specific lane index."""
        seg = self.get_segment_at(y)
        _, left, right = self.get_road_bounds(y)
        lanes = max(1, seg.lanes)
        lane_w = (right - left) / lanes
        lane_idx_clamped = max(0, min(lanes - 1, lane_idx))
        return left + (lane_idx_clamped * lane_w) + (lane_w / 2.0)

    def render(self, surface: pygame.Surface, camera, theme):
        """Render scrolling road surface, curbs, boundaries, and lane markings."""
        # 1. Fill ground shoulder terrain
        surface.fill(theme.ground_color)

        # 2. Render road in horizontal slice steps
        slice_height = 6
        num_slices = (camera.height // slice_height) + 4
        scroll_y = camera.world_y

        for i in range(num_slices):
            screen_y = i * slice_height
            wy = scroll_y + (camera.height * 0.78 - screen_y)

            seg = self.get_segment_at(wy)
            center_x, left_x, right_x = self.get_road_bounds(wy)
            sx_center, _ = camera.world_to_screen(center_x, wy)
            half_w = (right_x - left_x) / 2.0
            sx_left = sx_center - half_w
            sx_right = sx_center + half_w

            # Alternating red-white rumble curbs pattern
            curb_pattern = int(wy / 30.0) % 2 == 0
            curb_color = (235, 45, 45) if curb_pattern else (245, 245, 250)

            # Left & Right Curbs
            pygame.draw.rect(surface, curb_color, (int(sx_left - CURB_WIDTH), screen_y, CURB_WIDTH, slice_height))
            pygame.draw.rect(surface, curb_color, (int(sx_right), screen_y, CURB_WIDTH, slice_height))

            # Main Asphalt Road Body
            asphalt_rect = pygame.Rect(int(sx_left), screen_y, int(right_x - left_x), slice_height)
            pygame.draw.rect(surface, theme.asphalt_color, asphalt_rect)

            # Outer Solid Edge Lines (Roadside boundary)
            pygame.draw.line(surface, (230, 230, 240), (int(sx_left + 2), screen_y), (int(sx_left + 2), screen_y + slice_height), 2)
            pygame.draw.line(surface, (230, 230, 240), (int(sx_right - 2), screen_y), (int(sx_right - 2), screen_y + slice_height), 2)

            # Dashed Lane Markings
            is_stripe = (int(wy) % (STRIPE_LENGTH + STRIPE_GAP)) < STRIPE_LENGTH
            if is_stripe:
                lanes = max(1, seg.lanes)
                lane_width = (right_x - left_x) / lanes
                for l in range(1, lanes):
                    lx = int(sx_left + (l * lane_width))
                    col = COLOR_YELLOW if l == lanes // 2 else COLOR_WHITE
                    pygame.draw.line(surface, col, (lx, screen_y), (lx, screen_y + slice_height), 2)

        # 3. Weather FX (Rain in RAIN biome)
        if theme.has_rain:
            self._render_rain(surface)

    def _render_rain(self, surface: pygame.Surface):
        """Render fast falling rain drops."""
        dt = 0.016
        for drop in self.rain_drops:
            drop[1] += drop[2] * dt
            drop[0] += 60.0 * dt  # slight slant
            if drop[1] > VIRTUAL_HEIGHT:
                drop[1] = -drop[3]
                drop[0] = random.uniform(0, VIRTUAL_WIDTH)
            pygame.draw.line(surface, (180, 220, 255, 140), (int(drop[0]), int(drop[1])),
                             (int(drop[0] + 2), int(drop[1] + drop[3])), 1)


# Compatibility Alias
RoadSystem = RoadManager
