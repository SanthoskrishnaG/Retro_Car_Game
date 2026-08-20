"""Level Editor, Track Definition, and Custom Level (.rrlevel / JSON) Loader."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

from retro_racer.config import (
    TRACKS_DIR, ROAD_WIDTH, ROAD_LANES,
    BIOME_CITY, BIOME_COUNTRYSIDE, BIOME_DESERT,
    BIOME_MOUNTAIN, BIOME_NIGHT, BIOME_RAIN, BIOME_SYNTHWAVE
)


@dataclass
class TrackSegment:
    """Represents a discrete segment of road geometry."""
    length: float = 1200.0          # Segment distance in pixels
    curve: float = 0.0              # -1.0 (Hard Left) to +1.0 (Hard Right)
    road_width: int = ROAD_WIDTH    # Pixels width
    lanes: int = ROAD_LANES         # Number of lanes
    biome: str = BIOME_CITY         # Scenery biome
    traffic_density: float = 1.0    # Spawning multiplier
    hazard_rate: float = 0.2        # Probability of oil / cones
    scenery_left: str = "scenery_oak_tree"
    scenery_right: str = "scenery_street_lamp"

    @property
    def environment(self) -> str:
        return self.biome


@dataclass
class TrackData:
    """Full level and circuit configuration container."""
    name: str
    description: str = ""
    road_width: int = ROAD_WIDTH
    lanes: int = ROAD_LANES
    target_distance: float = 5000.0
    traffic_density: float = 1.0
    enemy_speed_multiplier: float = 1.0
    environment: str = BIOME_CITY
    weather: str = "clear"
    difficulty: str = "Medium"
    fuel_availability: float = 1.0
    powerup_frequency: float = 1.0
    checkpoints: List[float] = field(default_factory=lambda: [1500.0, 3000.0, 4500.0])
    target_laps: int = 1
    segments: List[TrackSegment] = field(default_factory=list)

    @property
    def biome(self) -> str:
        return self.environment

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "road_width": self.road_width,
            "lanes": self.lanes,
            "target_distance": self.target_distance,
            "traffic_density": self.traffic_density,
            "enemy_speed_multiplier": self.enemy_speed_multiplier,
            "environment": self.environment,
            "weather": self.weather,
            "difficulty": self.difficulty,
            "fuel_availability": self.fuel_availability,
            "powerup_frequency": self.powerup_frequency,
            "checkpoints": self.checkpoints,
            "target_laps": self.target_laps,
            "segments": [asdict(s) for s in self.segments]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrackData":
        raw_segments = data.get("segments", [])
        segments = []
        for s in raw_segments:
            # Handle aliases
            if "road_width" not in s and "width" in s:
                s["road_width"] = s["width"]
            if "biome" not in s and "environment" in s:
                s["biome"] = s["environment"]
            valid_keys = {k: v for k, v in s.items() if k in TrackSegment.__dataclass_fields__}
            segments.append(TrackSegment(**valid_keys))

        env = data.get("environment") or data.get("biome", BIOME_CITY)
        return cls(
            name=data.get("name", "Custom Level"),
            description=data.get("description", ""),
            road_width=data.get("road_width", ROAD_WIDTH),
            lanes=data.get("lanes", ROAD_LANES),
            target_distance=data.get("target_distance", 5000.0),
            traffic_density=data.get("traffic_density", 1.0),
            enemy_speed_multiplier=data.get("enemy_speed_multiplier", 1.0),
            environment=env,
            weather=data.get("weather", "clear"),
            difficulty=data.get("difficulty", "Medium"),
            fuel_availability=data.get("fuel_availability", 1.0),
            powerup_frequency=data.get("powerup_frequency", 1.0),
            checkpoints=data.get("checkpoints", [1500.0, 3000.0, 4500.0]),
            target_laps=data.get("target_laps", 1),
            segments=segments
        )


class LevelEditor:
    """Level Editor, Track Importer/Exporter for .rrlevel and .json level files."""

    def __init__(self, tracks_dir: Path = TRACKS_DIR):
        self.tracks_dir = tracks_dir
        self.tracks_dir.mkdir(parents=True, exist_ok=True)
        self.generate_default_tracks()

    def generate_default_tracks(self):
        """Create official 5-level campaign presets and custom circuits."""
        # Level 1 — City Rush
        lvl1 = TrackData(
            name="Level 1 — City Rush",
            description="High-speed sprint through the downtown metropolis with wide lanes and steady traffic.",
            road_width=ROAD_WIDTH,
            lanes=4,
            target_distance=5000.0,
            traffic_density=0.7,
            enemy_speed_multiplier=0.9,
            environment=BIOME_CITY,
            weather="clear",
            difficulty="Easy",
            fuel_availability=1.2,
            powerup_frequency=1.2,
            checkpoints=[1200.0, 2500.0, 3800.0, 4800.0],
            segments=[
                TrackSegment(length=1200.0, curve=0.0, scenery_left="scenery_building_1", scenery_right="scenery_street_lamp"),
                TrackSegment(length=1000.0, curve=0.25, scenery_left="scenery_oak_tree", scenery_right="scenery_building_2"),
                TrackSegment(length=1400.0, curve=-0.3, scenery_left="scenery_building_2", scenery_right="scenery_oak_tree"),
                TrackSegment(length=1400.0, curve=0.0, scenery_left="scenery_building_1", scenery_right="scenery_grandstand"),
            ]
        )
        self.save_track(lvl1)
        self.save_rrlevel(lvl1)

        # Level 2 — Green Valley
        lvl2 = TrackData(
            name="Level 2 — Green Valley",
            description="Rolling countryside highway with rain slick asphalt and sweeping curves.",
            road_width=ROAD_WIDTH,
            lanes=4,
            target_distance=6000.0,
            traffic_density=0.9,
            enemy_speed_multiplier=1.0,
            environment=BIOME_RAIN,
            weather="rain",
            difficulty="Medium",
            fuel_availability=1.0,
            powerup_frequency=1.0,
            checkpoints=[1500.0, 3000.0, 4500.0, 5800.0],
            segments=[
                TrackSegment(length=1400.0, curve=0.0, scenery_left="scenery_oak_tree", scenery_right="scenery_billboard_retro"),
                TrackSegment(length=1200.0, curve=0.45, scenery_left="scenery_oak_tree", scenery_right="scenery_oak_tree"),
                TrackSegment(length=1500.0, curve=-0.5, scenery_left="scenery_billboard_nitro", scenery_right="scenery_oak_tree"),
                TrackSegment(length=1900.0, curve=0.0, scenery_left="scenery_oak_tree", scenery_right="scenery_grandstand"),
            ]
        )
        self.save_track(lvl2)
        self.save_rrlevel(lvl2)

        # Level 3 — Desert Highway
        lvl3 = TrackData(
            name="Level 3 — Desert Highway",
            description="Blistering hot desert pass with cacti hazards and aggressive speeders.",
            road_width=ROAD_WIDTH,
            lanes=4,
            target_distance=6500.0,
            traffic_density=1.1,
            enemy_speed_multiplier=1.15,
            environment=BIOME_DESERT,
            weather="clear",
            difficulty="Hard",
            fuel_availability=0.9,
            powerup_frequency=0.9,
            checkpoints=[1600.0, 3200.0, 4800.0, 6200.0],
            segments=[
                TrackSegment(length=1200.0, curve=0.0, scenery_left="scenery_cactus", scenery_right="scenery_rock"),
                TrackSegment(length=1400.0, curve=-0.65, scenery_left="scenery_rock", scenery_right="scenery_cactus", hazard_rate=0.4),
                TrackSegment(length=1100.0, curve=0.75, scenery_left="scenery_cactus", scenery_right="scenery_rock", hazard_rate=0.5),
                TrackSegment(length=1600.0, curve=-0.3, scenery_left="scenery_rock", scenery_right="scenery_cactus"),
                TrackSegment(length=1200.0, curve=0.0, scenery_left="scenery_cactus", scenery_right="scenery_grandstand"),
            ]
        )
        self.save_track(lvl3)
        self.save_rrlevel(lvl3)

        # Level 4 — Mountain Road
        lvl4 = TrackData(
            name="Level 4 — Mountain Road",
            description="Narrow mountain pass with pine forests, aggressive lane changers, and steep switchbacks.",
            road_width=170,
            lanes=3,
            target_distance=7000.0,
            traffic_density=1.2,
            enemy_speed_multiplier=1.2,
            environment=BIOME_MOUNTAIN,
            weather="clear",
            difficulty="Expert",
            fuel_availability=0.85,
            powerup_frequency=0.85,
            checkpoints=[1800.0, 3600.0, 5400.0, 6800.0],
            segments=[
                TrackSegment(length=1200.0, curve=0.0, road_width=170, lanes=3, scenery_left="scenery_pine_tree", scenery_right="scenery_pine_tree"),
                TrackSegment(length=1300.0, curve=0.6, road_width=170, lanes=3, scenery_left="scenery_pine_tree", scenery_right="scenery_rock"),
                TrackSegment(length=1400.0, curve=-0.65, road_width=170, lanes=3, scenery_left="scenery_rock", scenery_right="scenery_pine_tree"),
                TrackSegment(length=1300.0, curve=0.4, road_width=170, lanes=3, scenery_left="scenery_pine_tree", scenery_right="scenery_grandstand"),
            ]
        )
        self.save_track(lvl4)
        self.save_rrlevel(lvl4)

        # Level 5 — Night Drive
        lvl5 = TrackData(
            name="Level 5 — Night Drive",
            description="Midnight synthwave freeway with glowing skyscrapers and hyper-fast traffic.",
            road_width=ROAD_WIDTH,
            lanes=4,
            target_distance=8000.0,
            traffic_density=1.35,
            enemy_speed_multiplier=1.3,
            environment=BIOME_SYNTHWAVE,
            weather="clear",
            difficulty="Master",
            fuel_availability=0.8,
            powerup_frequency=0.8,
            checkpoints=[2000.0, 4000.0, 6000.0, 7800.0],
            segments=[
                TrackSegment(length=1400.0, curve=0.0, scenery_left="scenery_billboard_retro", scenery_right="scenery_street_lamp"),
                TrackSegment(length=1200.0, curve=0.35, scenery_left="scenery_billboard_nitro", scenery_right="scenery_palm_tree"),
                TrackSegment(length=1600.0, curve=-0.4, scenery_left="scenery_street_lamp", scenery_right="scenery_building_1"),
                TrackSegment(length=1400.0, curve=0.2, scenery_left="scenery_palm_tree", scenery_right="scenery_grandstand"),
                TrackSegment(length=1800.0, curve=0.0, scenery_left="scenery_billboard_retro", scenery_right="scenery_street_lamp"),
            ]
        )
        self.save_track(lvl5)
        self.save_rrlevel(lvl5)

    def save_track(self, track: TrackData) -> Path:
        """Save a track to JSON file."""
        clean_name = track.name.lower().replace(" ", "_").replace("—", "-")
        filename = f"{clean_name}.json"
        path = self.tracks_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(track.to_dict(), f, indent=2)
        return path

    def save_rrlevel(self, track: TrackData) -> Path:
        """Save track in custom .rrlevel format."""
        clean_name = track.name.lower().replace(" ", "_").replace("—", "-")
        filename = f"{clean_name}.rrlevel"
        path = self.tracks_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(track.to_dict(), f, indent=2)
        return path

    def load_track(self, filename: str) -> Optional[TrackData]:
        """Load track from JSON or .rrlevel file."""
        path = self.tracks_dir / filename
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return TrackData.from_dict(data)

    def list_tracks(self) -> List[TrackData]:
        """List all available track files (.json and .rrlevel)."""
        tracks = []
        seen_names = set()
        for pattern in ["*.json", "*.rrlevel"]:
            for file in sorted(self.tracks_dir.glob(pattern)):
                try:
                    t = self.load_track(file.name)
                    if t and t.name not in seen_names:
                        tracks.append(t)
                        seen_names.add(t.name)
                except Exception:
                    continue
        return tracks
