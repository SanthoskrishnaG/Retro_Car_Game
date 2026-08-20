"""Unit tests for replay recording, JSON serialization, and playback timeline."""

import pytest
from pathlib import Path
from retro_racer.systems.replay import ReplayManager


@pytest.fixture
def replay_mgr(tmp_path):
    return ReplayManager(replays_dir=tmp_path)


def test_replay_recording_and_save(replay_mgr):
    replay_mgr.start_recording(track_name="Test Track", car_model="player_red", player_name="Test Driver")
    assert replay_mgr.is_recording

    # Record 10 frames
    for i in range(10):
        replay_mgr.record_frame({"player_x": 240 + i, "player_y": i * 10, "speed": 200.0, "score": i * 100})

    saved_path = replay_mgr.stop_recording(final_score=1000, final_distance=100.0)
    assert saved_path is not None
    assert saved_path.exists()
    assert not replay_mgr.is_recording


def test_replay_load_and_playback(replay_mgr):
    replay_mgr.start_recording(track_name="Test Track", car_model="player_red", player_name="Test Driver")
    for i in range(20):
        replay_mgr.record_frame({"player_x": 240, "player_y": i * 10, "speed": 200.0})
    saved_path = replay_mgr.stop_recording(final_score=2000, final_distance=200.0)

    # Load back
    loaded = replay_mgr.load_replay(saved_path)
    assert loaded
    assert len(replay_mgr.frames) == 20
    assert replay_mgr.is_playing

    # Advance
    replay_mgr.advance_playback(dt=0.05)
    assert replay_mgr.current_frame > 0

    # Seek
    replay_mgr.seek(15)
    assert replay_mgr.current_frame == 15
