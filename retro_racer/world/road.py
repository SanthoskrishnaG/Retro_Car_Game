"""Segment-based Curved Road System and Asphalt Rendering."""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
import pygame

from retro_racer.config import (
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, ROAD_LANES, LANE_WIDTH, ROAD_WIDTH,
    ROAD_CENTER_X, ROAD_LEFT_EDGE, ROAD_RIGHT_EDGE, STRIPE_LENGTH, STRIPE_GAP,
    CURB_WIDTH, COLOR_ASPHALT, COLOR_ROAD_EDGE, COLOR_WHITE, COLOR_YELLOW,
    COLOR_RED
)
from retro_racer.systems.level_editor import TrackData, TrackSegment


@dataclass
class RoadSegmentGeometry:
    start_y: float
    end_y: float
    curve: float
    road_width: int
    biome: str
    scenery_left: str = "scenery_oak_tree"
    scenery_right: str = "scenery_street_lamp"


class RoadSystem:
    """Manages road geometry, lane positions, curvature lookup, and track rendering."""

    def __init__(self, track_data: Optional[TrackData] = None):
        self.segments: List[RoadSegmentGeometry] = []
        self.total_length: float = 10000.0
        self.track_name: str = "Default Track"
        self.biome: str = "city_day"

        if track_data:
            self.load_track(track_data)
        else:
            self._generate_default_geometry()

    def load_track(self, track: TrackData):
        """Build continuous geometric segments from TrackData."""
        self.track_name = track.name
        self.biome = track.biome
        self.segments.clear()

        curr_y = 0.0
        for seg in track.segments:
            geom = RoadSegmentGeometry(
                start_y=curr_y,
                end_y=curr_y + seg.length,
                curve=seg.curve,
                road_width=seg.road_width,
                biome=seg.biome,
                scenery_left=getattr(seg, "scenery_left", "scenery_oak_tree"),
                scenery_right=getattr(seg, "scenery_right", "scenery_street_lamp")
            )
            self.segments.append(geom)
            curr_y += seg.length

        self.total_length = max(1000.0, curr_y)

    def _generate_default_geometry(self):
        """Fallback default 4-segment loop."""
        self.segments = [
            RoadSegmentGeometry(0.0, 1500.0, 0.0, 272, "city_day", "scenery_oak_tree", "scenery_street_lamp"),
            RoadSegmentGeometry(1500.0, 3000.0, 0.35, 272, "city_day", "scenery_palm_tree", "scenery_billboard_retro"),
            RoadSegmentGeometry(3000.0, 4500.0, -0.4, 272, "city_day", "scenery_building_1", "scenery_street_lamp"),
            RoadSegmentGeometry(4500.0, 6000.0, 0.0, 272, "city_day", "scenery_oak_tree", "scenery_grandstand"),
        ]
        self.total_length = 6000.0

    def get_segment_at(self, y: float) -> RoadSegmentGeometry:
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
        half_w = seg.road_width / 2.0
        # Lateral offset from curve integration
        curve_offset = seg.curve * 20.0
        center_x = ROAD_CENTER_X + curve_offset
        return center_x, center_x - half_w, center_x + half_w

    def get_lane_center_x(self, lane_idx: int, y: float) -> float:
        """Get lateral center coordinate for a specific lane index (0 to 3)."""
        _, left, right = self.get_road_bounds(y)
        lane_w = (right - left) / ROAD_LANES
        return left + (lane_idx * lane_w) + (lane_w / 2.0)

    def render(self, surface: pygame.Surface, camera, theme):
        """Render scrolling road surface, curbs, and lane markings."""
        # 1. Fill ground shoulder terrain
        surface.fill(theme.ground_color)

        # 2. Render road in horizontal slice steps (for curvature pseudo-perspective)
        slice_height = 8
        num_slices = (camera.height // slice_height) + 4

        # Calculate base scroll offset
        scroll_y = camera.world_y

        for i in range(num_slices):
            screen_y = i * slice_height
            # World distance corresponding to this screen Y
            wy = scroll_y + (camera.height * 0.78 - screen_y)

            # Get geometry
            center_x, left_x, right_x = self.get_road_bounds(wy)
            # Transform to camera screen coordinates
            sx_center, _ = camera.world_to_screen(center_x, wy)
            half_w = (right_x - left_x) / 2.0
            sx_left = sx_center - half_w
            sx_right = sx_center + half_w

            # Alternating red-white rumble curbs pattern based on distance
            curb_pattern = int(wy / 40.0) % 2 == 0
            curb_color = (235, 45, 45) if curb_pattern else (245, 245, 250)

            # Left Curb
            pygame.draw.rect(surface, curb_color, (int(sx_left - CURB_WIDTH), screen_y, CURB_WIDTH, slice_height))
            # Right Curb
            pygame.draw.rect(surface, curb_color, (int(sx_right), screen_y, CURB_WIDTH, slice_height))

            # Main Asphalt Road Body
            asphalt_rect = pygame.Rect(int(sx_left), screen_y, int(right_x - left_x), slice_height)
            pygame.draw.rect(surface, theme.asphalt_color, asphalt_rect)

            # Outer Solid Edge Lines
            pygame.draw.line(surface, (230, 230, 240), (int(sx_left + 2), screen_y), (int(sx_left + 2), screen_y + slice_height), 2)
            pygame.draw.line(surface, (230, 230, 240), (int(sx_right - 2), screen_y), (int(sx_right - 2), screen_y + slice_height), 2)

            # Dashed Lane Markings (White dashes with scrolling gap)
            is_stripe = (int(wy) % (STRIPE_LENGTH + STRIPE_GAP)) < STRIPE_LENGTH
            if is_stripe:
                lane_width = (right_x - left_x) / ROAD_LANES
                # Lane divider 1 (between lane 0 and 1)
                d1_x = int(sx_left + lane_width)
                pygame.draw.line(surface, COLOR_WHITE, (d1_x, screen_y), (d1_x, screen_y + slice_height), 2)

                # Center dual median divider (between lane 1 and 2)
                d2_x = int(sx_center)
                pygame.draw.line(surface, COLOR_YELLOW, (d2_x - 1, screen_y), (d2_x - 1, screen_y + slice_height), 2)

                # Lane divider 3 (between lane 2 and 3)
                d3_x = int(sx_right - lane_width)
                pygame.draw.line(surface, COLOR_WHITE, (d3_x, screen_y), (d3_x, screen_y + slice_height), 2)
