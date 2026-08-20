"""Unit tests for Level Editor, 5 Campaign Levels, RoadManager, and .rrlevel format."""

import pytest
from pathlib import Path
from retro_racer.systems.level_editor import LevelEditor, TrackData, TrackSegment
from retro_racer.world.road import RoadManager, RoadSegment
from retro_racer.world.environment import get_environment_theme, THEMES
from retro_racer.entities.traffic import TrafficCar, EnemyBehavior


@pytest.fixture
def level_editor(tmp_path):
    return LevelEditor(tracks_dir=tmp_path)


def test_five_campaign_levels_generation(level_editor):
    tracks = level_editor.list_tracks()
    track_names = [t.name for t in tracks]

    assert any("City Rush" in name for name in track_names)
    assert any("Green Valley" in name for name in track_names)
    assert any("Desert Highway" in name for name in track_names)
    assert any("Mountain Road" in name for name in track_names)
    assert any("Night Drive" in name for name in track_names)


def test_custom_rrlevel_save_and_load(level_editor):
    track = TrackData(
        name="Custom Grand Prix",
        description="Circuit test with .rrlevel extension",
        road_width=180,
        lanes=4,
        target_distance=5500.0,
        traffic_density=0.8,
        enemy_speed_multiplier=1.1,
        environment="city",
        weather="clear",
        difficulty="Hard",
        fuel_availability=1.0,
        powerup_frequency=1.0,
        checkpoints=[1500.0, 3000.0, 4500.0],
        segments=[
            TrackSegment(length=1200.0, curve=0.3),
            TrackSegment(length=1500.0, curve=-0.4)
        ]
    )

    path = level_editor.save_rrlevel(track)
    assert path.suffix == ".rrlevel"
    assert path.exists()

    loaded = level_editor.load_track(path.name)
    assert loaded is not None
    assert loaded.name == "Custom Grand Prix"
    assert loaded.target_distance == 5500.0
    assert loaded.checkpoints == [1500.0, 3000.0, 4500.0]
    assert len(loaded.segments) == 2


def test_environment_themes_and_presets():
    for biome in ["city", "countryside", "desert", "mountain", "night", "rain", "synthwave"]:
        theme = get_environment_theme(biome)
        assert theme is not None
        assert len(theme.ground_color) == 3
        assert len(theme.asphalt_color) == 3


def test_road_manager_segments_and_boundaries():
    track = TrackData(
        name="Rain Mountain Pass",
        description="Twisty mountain in rain",
        environment="rain",
        target_laps=1,
        difficulty="Hard",
        segments=[
            TrackSegment(length=1000.0, curve=0.0),
            TrackSegment(length=1200.0, curve=-0.4),
        ]
    )
    road_mgr = RoadManager(track)
    assert road_mgr.total_length == 2200.0
    assert road_mgr.get_curvature_at(500.0) == 0.0
    assert road_mgr.get_curvature_at(1500.0) == -0.4

    center_x, left, right = road_mgr.get_road_bounds(500.0)
    assert left < center_x < right


def test_deterministic_enemy_traffic_ai_seeding():
    t1 = TrafficCar(160.0, 300.0, EnemyBehavior.LANE_CHANGER, lane_idx=1, seed=42)
    t2 = TrafficCar(160.0, 300.0, EnemyBehavior.LANE_CHANGER, lane_idx=1, seed=42)

    assert t1.speed == t2.speed
    assert t1.lane_change_timer == t2.lane_change_timer
    assert t1.health == t2.health

    for _ in range(10):
        t1.update_ai(0.05, [t1])
        t2.update_ai(0.05, [t2])

    assert t1.position_x == t2.position_x
    assert t1.position_y == t2.position_y
