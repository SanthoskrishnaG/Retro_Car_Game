"""Environment themes, color palettes, and biome presets."""

from typing import Tuple
from dataclasses import dataclass

from retro_racer.config import (
    BIOME_CITY_DAY, BIOME_CITY_NIGHT, BIOME_SYNTHWAVE,
    BIOME_DESERT, BIOME_ALPINE
)


@dataclass
class EnvironmentTheme:
    name: str
    ground_color: Tuple[int, int, int]
    asphalt_color: Tuple[int, int, int]
    edge_color: Tuple[int, int, int]
    sky_color: Tuple[int, int, int]
    is_night: bool = False


THEMES = {
    BIOME_CITY_DAY: EnvironmentTheme(
        name="City Day",
        ground_color=(45, 145, 65),       # Vibrant grassy park
        asphalt_color=(55, 60, 72),       # Slate gray asphalt
        edge_color=(75, 82, 98),
        sky_color=(120, 180, 240)
    ),
    BIOME_CITY_NIGHT: EnvironmentTheme(
        name="City Night",
        ground_color=(20, 24, 34),        # Midnight city ground
        asphalt_color=(38, 42, 52),       # Dark charcoal road
        edge_color=(50, 56, 70),
        sky_color=(15, 18, 28),
        is_night=True
    ),
    BIOME_SYNTHWAVE: EnvironmentTheme(
        name="Synthwave Grid",
        ground_color=(32, 12, 48),        # Deep purple synth ground
        asphalt_color=(45, 25, 65),       # Neon indigo highway
        edge_color=(180, 40, 220),
        sky_color=(25, 10, 40),
        is_night=True
    ),
    BIOME_DESERT: EnvironmentTheme(
        name="Desert Canyon",
        ground_color=(215, 175, 115),     # Warm golden sand
        asphalt_color=(85, 78, 70),       # Dusty desert highway
        edge_color=(120, 110, 95),
        sky_color=(240, 180, 110)
    ),
    BIOME_ALPINE: EnvironmentTheme(
        name="Alpine Ridge",
        ground_color=(30, 85, 45),        # Deep evergreen ridge
        asphalt_color=(48, 52, 60),       # Cold mountain asphalt
        edge_color=(65, 70, 80),
        sky_color=(160, 200, 230)
    ),
}


def get_environment_theme(biome_name: str) -> EnvironmentTheme:
    """Retrieve theme config for biome."""
    return THEMES.get(biome_name, THEMES[BIOME_CITY_DAY])
