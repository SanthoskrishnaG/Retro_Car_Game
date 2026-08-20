"""Level Editor and Track Definition Manager for Retro Racer Python."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from retro_racer.config import TRACKS_DIR, BIOME_SYNTHWAVE, BIOME_DESERT, BIOME_ALPINE, BIOME_CITY_DAY, BIOME_CITY_NIGHT


@dataclass
class TrackSegment:
    """Represents a discrete segment of road geometry."""
    length: float = 1200.0          # Segment distance in pixels
    curve: float = 0.0              # -1.0 (Hard Left) to +1.0 (Hard Right)
    road_width: int = 272           # Pixels width
    biome: str = BIOME_CITY_DAY     # Scenery biome
    traffic_density: float = 1.0    # Spawning multiplier
    hazard_rate: float = 0.2        # Probability of oil / cones
    scenery_left: str = "scenery_oak_tree"
    scenery_right: str = "scenery_street_lamp"


@dataclass
class TrackData:
    """Full track configuration container."""
    name: str
    description: str
    biome: str
    target_laps: int
    difficulty: str
    segments: List[TrackSegment]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "biome": self.biome,
            "target_laps": self.target_laps,
            "difficulty": self.difficulty,
            "segments": [asdict(s) for s in self.segments]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrackData":
        segments = [TrackSegment(**s) for s in data.get("segments", [])]
        return cls(
            name=data.get("name", "Custom Track"),
            description=data.get("description", ""),
            biome=data.get("biome", BIOME_CITY_DAY),
            target_laps=data.get("target_laps", 1),
            difficulty=data.get("difficulty", "Medium"),
            segments=segments
        )


class LevelEditor:
    """Level Editor logic, track importer/exporter, and default track generator."""

    def __init__(self, tracks_dir: Path = TRACKS_DIR):
        self.tracks_dir = tracks_dir
        self.tracks_dir.mkdir(parents=True, exist_ok=True)
        self.generate_default_tracks()

    def generate_default_tracks(self):
        """Create built-in track presets if they don't exist."""
        # 1. Neon Synthwave Circuit
        synthwave_track = TrackData(
            name="Synthwave Boulevard",
            description="High-speed neon highway with sweeping curves and glowing billboards.",
            biome=BIOME_SYNTHWAVE,
            target_laps=1,
            difficulty="Easy",
            segments=[
                TrackSegment(length=1400.0, curve=0.0, scenery_left="scenery_billboard_retro", scenery_right="scenery_street_lamp"),
                TrackSegment(length=1200.0, curve=0.35, scenery_left="scenery_billboard_nitro", scenery_right="scenery_palm_tree"),
                TrackSegment(length=1600.0, curve=-0.4, scenery_left="scenery_street_lamp", scenery_right="scenery_building_1"),
                TrackSegment(length=1400.0, curve=0.2, scenery_left="scenery_palm_tree", scenery_right="scenery_grandstand"),
                TrackSegment(length=1800.0, curve=0.0, scenery_left="scenery_billboard_retro", scenery_right="scenery_street_lamp"),
            ]
        )
        self.save_track(synthwave_track)

        # 2. Desert Canyon Rally
        desert_track = TrackData(
            name="Desert Canyon Rally",
            description="Twisting canyon road with sharp bends, road obstacles, and blinding heat.",
            biome=BIOME_DESERT,
            target_laps=1,
            difficulty="Hard",
            segments=[
                TrackSegment(length=1200.0, curve=0.0, scenery_left="scenery_cactus", scenery_right="scenery_rock"),
                TrackSegment(length=1400.0, curve=-0.7, scenery_left="scenery_rock", scenery_right="scenery_cactus", hazard_rate=0.4),
                TrackSegment(length=1000.0, curve=0.8, scenery_left="scenery_cactus", scenery_right="scenery_rock", hazard_rate=0.5),
                TrackSegment(length=1500.0, curve=-0.3, scenery_left="scenery_rock", scenery_right="scenery_cactus"),
                TrackSegment(length=1200.0, curve=0.0, scenery_left="scenery_cactus", scenery_right="scenery_grandstand"),
            ]
        )
        self.save_track(desert_track)

        # 3. Alpine Mountain Pass
        alpine_track = TrackData(
            name="Alpine Ridge Pass",
            description="Narrow mountain pass with pine forests, aggressive lane changers, and steep switchbacks.",
            biome=BIOME_ALPINE,
            target_laps=1,
            difficulty="Expert",
            segments=[
                TrackSegment(length=1200.0, curve=0.0, road_width=250, scenery_left="scenery_pine_tree", scenery_right="scenery_pine_tree"),
                TrackSegment(length=1300.0, curve=0.6, road_width=240, scenery_left="scenery_pine_tree", scenery_right="scenery_rock"),
                TrackSegment(length=1400.0, curve=-0.65, road_width=240, scenery_left="scenery_rock", scenery_right="scenery_pine_tree"),
                TrackSegment(length=1200.0, curve=0.4, road_width=260, scenery_left="scenery_pine_tree", scenery_right="scenery_grandstand"),
            ]
        )
        self.save_track(alpine_track)

        # 4. Metropolis Highway
        city_track = TrackData(
            name="Metropolis Highway",
            description="Dense 4-lane city arterial with heavy semi-truck traffic and speedy sedans.",
            biome=BIOME_CITY_DAY,
            target_laps=1,
            difficulty="Medium",
            segments=[
                TrackSegment(length=1500.0, curve=0.0, scenery_left="scenery_building_1", scenery_right="scenery_building_2", traffic_density=1.4),
                TrackSegment(length=1200.0, curve=0.25, scenery_left="scenery_oak_tree", scenery_right="scenery_building_1", traffic_density=1.3),
                TrackSegment(length=1400.0, curve=-0.3, scenery_left="scenery_building_2", scenery_right="scenery_oak_tree", traffic_density=1.5),
                TrackSegment(length=1600.0, curve=0.0, scenery_left="scenery_building_1", scenery_right="scenery_grandstand"),
            ]
        )
        self.save_track(city_track)

    def save_track(self, track: TrackData) -> Path:
        """Save a track to JSON file."""
        filename = f"{track.name.lower().replace(' ', '_')}.json"
        path = self.tracks_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(track.to_dict(), f, indent=2)
        return path

    def load_track(self, filename: str) -> Optional[TrackData]:
        """Load track from JSON filename."""
        path = self.tracks_dir / filename
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return TrackData.from_dict(data)

    def list_tracks(self) -> List[TrackData]:
        """List all available track files."""
        tracks = []
        for file in sorted(self.tracks_dir.glob("*.json")):
            try:
                t = self.load_track(file.name)
                if t:
                    tracks.append(t)
            except Exception:
                continue
        return tracks
