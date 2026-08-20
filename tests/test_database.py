"""Unit tests for SQLite database persistence, high scores, and garage stats."""

import pytest
from pathlib import Path
from retro_racer.systems.database import Database


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_retro_racer.db"
    return Database(db_path=db_file)


def test_db_schema_initialization(temp_db):
    profile = temp_db.get_career_profile()
    assert profile["credits"] == 500
    assert profile["player_name"] == "Racer 1"


def test_add_and_retrieve_high_scores(temp_db):
    temp_db.add_high_score("SpeedDemon", 45000, 1200.5, "Synthwave Boulevard", "player_red")
    temp_db.add_high_score("TurboKing", 89000, 2400.0, "Synthwave Boulevard", "player_cyan")

    scores = temp_db.get_top_scores(limit=5)
    assert len(scores) == 2
    assert scores[0]["player_name"] == "TurboKing"
    assert scores[0]["score"] == 89000


def test_career_stat_updates(temp_db):
    temp_db.update_career_stats(added_credits=300, distance=500.0)
    profile = temp_db.get_career_profile()
    assert profile["credits"] == 800
    assert profile["total_distance"] == 500.0
    assert profile["total_races"] == 1


def test_purchase_upgrades(temp_db):
    success = temp_db.purchase_upgrade("top_speed", cost=250)
    assert success
    profile = temp_db.get_career_profile()
    assert profile["upgrade_top_speed"] == 1
    assert profile["credits"] == 250

    # Fail if insufficient credits
    failed = temp_db.purchase_upgrade("top_speed", cost=500)
    assert not failed


def test_unlock_car(temp_db):
    temp_db.update_career_stats(added_credits=1000, distance=0)
    assert not temp_db.is_car_unlocked("player_yellow")

    unlocked = temp_db.unlock_car("player_yellow", cost=600)
    assert unlocked
    assert temp_db.is_car_unlocked("player_yellow")
