"""Unit tests for Level Editor, Track JSON serialization, and Road Geometry."""

import pytest
from pathlib import Path
from retro_racer.systems.level_editor import LevelEditor, TrackData, TrackSegment
from retro_racer.world.road import RoadSystem


@pytest.fixture
def level_editor(tmp_path):
    return LevelEditor(tracks_dir=tmp_path)


def test_default_tracks_creation(level_editor):
    tracks = level_editor.list_tracks()
    assert len(tracks) >= 4
    names = [t.name for t in tracks]
    assert "Synthwave Boulevard" in names
    assert "Desert Canyon Rally" in names


def test_custom_track_save_and_load(level_editor):
    track = TrackData(
        name="Hyperloop Speedways",
        description="Speed circuit",
        biome="synthwave",
        target_laps=1,
        difficulty="Extreme",
        segments=[
            TrackSegment(length=1000.0, curve=0.0),
            TrackSegment(length=1500.0, curve=0.6),
        ]
    )
    saved_path = level_editor.save_track(track)
    assert saved_path.exists()

    loaded = level_editor.load_track(saved_path.name)
    assert loaded.name == "Hyperloop Speedways"
    assert len(loaded.segments) == 2
    assert loaded.segments[1].curve == 0.6


def test_road_system_curvature_and_bounds():
    track = TrackData(
        name="Curve Test",
        description="Testing curves",
        biome="city_day",
        target_laps=1,
        difficulty="Medium",
        segments=[
            TrackSegment(length=1000.0, curve=0.0),
            TrackSegment(length=1000.0, curve=0.5),
        ]
    )
    road = RoadSystem(track)
    assert road.get_curvature_at(500.0) == 0.0
    assert road.get_curvature_at(1500.0) == 0.5

    center_x, left, right = road.get_road_bounds(500.0)
    assert left < center_x < right
