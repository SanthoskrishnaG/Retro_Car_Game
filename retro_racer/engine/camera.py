"""Dynamic 2D Camera with pseudo-perspective curvature, tracking, and screen shake."""

import random
from typing import Tuple

from retro_racer.config import VIRTUAL_WIDTH, VIRTUAL_HEIGHT, ROAD_CENTER_X


class Camera:
    """Follows the race action, simulates curvature shift and manages screen shake."""

    def __init__(self, width: int = VIRTUAL_WIDTH, height: int = VIRTUAL_HEIGHT):
        self.width = width
        self.height = height
        self.world_y = 0.0
        self.target_x = float(ROAD_CENTER_X)
        self.x = float(ROAD_CENTER_X)

        # Screen Shake
        self.shake_intensity = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

        # Curvature dynamic banking
        self.curve_offset = 0.0

    def add_shake(self, intensity: float):
        """Trigger camera screen shake effect."""
        self.shake_intensity = min(25.0, self.shake_intensity + intensity)

    def update(self, dt: float, player_x: float, player_y: float, road_curve: float):
        """Update camera position, shake decay, and curvature shift."""
        # Follow player y-distance
        self.world_y = player_y

        # Smooth lateral camera pan
        self.target_x = ROAD_CENTER_X + (player_x - ROAD_CENTER_X) * 0.3
        self.x += (self.target_x - self.x) * min(1.0, dt * 8.0)

        # Curvature lateral banking shift
        target_curve_offset = road_curve * 45.0
        self.curve_offset += (target_curve_offset - self.curve_offset) * min(1.0, dt * 5.0)

        # Decay shake
        if self.shake_intensity > 0.01:
            self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity *= max(0.0, 1.0 - dt * 10.0)
        else:
            self.shake_intensity = 0.0
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0

    def world_to_screen(self, wx: float, wy: float) -> Tuple[int, int]:
        """Convert world coordinates to screen pixel coordinates."""
        # Vertical: road scrolls downward, player is near bottom (~75% screen height)
        sy = (self.height * 0.78) - (wy - self.world_y)
        # Horizontal: center offset + curvature shift + shake
        sx = wx - (self.x - self.width / 2) + self.curve_offset + self.shake_offset_x
        sy += self.shake_offset_y
        return int(sx), int(sy)

    def get_render_offset(self) -> Tuple[float, float]:
        """Get global renderer transform offset."""
        ox = -(self.x - self.width / 2) + self.curve_offset + self.shake_offset_x
        oy = self.shake_offset_y
        return ox, oy
