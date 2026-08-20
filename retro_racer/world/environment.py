"""Environment themes, color palettes, weather effects, and road presets."""

from typing import Tuple
from dataclasses import dataclass

from retro_racer.config import (
    BIOME_CITY, BIOME_COUNTRYSIDE, BIOME_DESERT,
    BIOME_MOUNTAIN, BIOME_NIGHT, BIOME_RAIN, BIOME_SYNTHWAVE
)


@dataclass
class EnvironmentTheme:
    name: str
    ground_color: Tuple[int, int, int]
    asphalt_color: Tuple[int, int, int]
    edge_color: Tuple[int, int, int]
    sky_color: Tuple[int, int, int]
    is_night: bool = False
    has_rain: bool = False


THEMES = {
    BIOME_CITY: EnvironmentTheme(
        name="City",
        ground_color=(45, 145, 65),       # Vibrant emerald lawn
        asphalt_color=(55, 60, 72),       # Dark slate road
        edge_color=(75, 82, 98),
        sky_color=(120, 180, 240)
    ),
    BIOME_COUNTRYSIDE: EnvironmentTheme(
        name="Countryside",
        ground_color=(60, 160, 50),       # Lush rolling fields
        asphalt_color=(50, 54, 62),       # Smooth rural asphalt
        edge_color=(70, 75, 85),
        sky_color=(135, 195, 250)
    ),
    BIOME_DESERT: EnvironmentTheme(
        name="Desert",
        ground_color=(215, 175, 115),     # Warm golden sand
        asphalt_color=(85, 78, 70),       # Dusty desert highway
        edge_color=(120, 110, 95),
        sky_color=(240, 180, 110)
    ),
    BIOME_MOUNTAIN: EnvironmentTheme(
        name="Mountain",
        ground_color=(35, 90, 48),        # Deep evergreen alpine ridge
        asphalt_color=(48, 52, 60),       # Cold mountain asphalt
        edge_color=(65, 70, 80),
        sky_color=(160, 200, 230)
    ),
    BIOME_NIGHT: EnvironmentTheme(
        name="Night",
        ground_color=(18, 22, 32),        # Midnight city ground
        asphalt_color=(34, 38, 48),       # Dark charcoal road
        edge_color=(48, 54, 68),
        sky_color=(12, 15, 24),
        is_night=True
    ),
    BIOME_RAIN: EnvironmentTheme(
        name="Rain Storm",
        ground_color=(28, 48, 38),        # Wet drenched dark turf
        asphalt_color=(28, 32, 42),       # Slick glossy wet asphalt
        edge_color=(45, 52, 65),
        sky_color=(45, 55, 70),
        has_rain=True
    ),
    BIOME_SYNTHWAVE: EnvironmentTheme(
        name="Synthwave",
        ground_color=(32, 12, 48),        # Deep purple synth ground
        asphalt_color=(45, 25, 65),       # Neon indigo highway
        edge_color=(180, 40, 220),
        sky_color=(25, 10, 40),
        is_night=True
    ),
}


def get_environment_theme(biome_name: str) -> EnvironmentTheme:
    """Retrieve theme config for biome with fallback."""
    # Normalize aliases
    norm = biome_name.lower().replace("city_day", "city").replace("city_night", "night").replace("alpine", "mountain")
    return THEMES.get(norm, THEMES.get(BIOME_CITY, THEMES[list(THEMES.keys())[0]]))
