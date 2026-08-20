"""Unit tests for Level Editor, RoadManager, and Environment types."""

import pytest
from pathlib import Path
from retro_racer.systems.level_editor import LevelEditor, TrackData, TrackSegment
from retro_racer.world.road import RoadManager, RoadSegment
from retro_racer.world.environment import get_environment_theme, THEMES
from retro_racer.entities.traffic import TrafficCar, EnemyBehavior


@pytest.fixture
def level_editor(tmp_path):
    return LevelEditor(tracks_dir=tmp_path)


def test_environment_themes_and_presets():
    # Verify all required road biomes
    for biome in ["city", "countryside", "desert", "mountain", "night", "rain", "synthwave"]:
        theme = get_environment_theme(biome)
        assert theme is not None
        assert len(theme.ground_color) == 3
        assert len(theme.asphalt_color) == 3


def test_road_manager_segments_and_boundaries():
    track = TrackData(
        name="Rain Mountain Pass",
        description="Twisty mountain in rain",
        biome="rain",
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
    # Two enemies with same seed must make identical decisions
    t1 = TrafficCar(160.0, 300.0, EnemyBehavior.LANE_CHANGER, lane_idx=1, seed=42)
    t2 = TrafficCar(160.0, 300.0, EnemyBehavior.LANE_CHANGER, lane_idx=1, seed=42)

    assert t1.speed == t2.speed
    assert t1.lane_change_timer == t2.lane_change_timer
    assert t1.health == t2.health

    # Step AI 10 frames
    for _ in range(10):
        t1.update_ai(0.05, [t1])
        t2.update_ai(0.05, [t2])

    assert t1.position_x == t2.position_x
    assert t1.position_y == t2.position_y
