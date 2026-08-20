"""SQLite database manager for persistent high scores, career profile, and garage upgrades."""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from retro_racer.config import DB_PATH


class Database:
    """Handles persistent storage using SQLite."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        """Initialize database tables if they do not exist."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # High Scores table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    distance REAL NOT NULL,
                    track_name TEXT NOT NULL,
                    car_model TEXT NOT NULL,
                    timestamp INTEGER NOT NULL
                )
            """)
            # Career Profile & Garage Upgrades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS career_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    player_name TEXT NOT NULL DEFAULT 'Racer 1',
                    credits INTEGER NOT NULL DEFAULT 500,
                    total_distance REAL NOT NULL DEFAULT 0.0,
                    total_races INTEGER NOT NULL DEFAULT 0,
                    selected_car TEXT NOT NULL DEFAULT 'player_red',
                    upgrade_top_speed INTEGER NOT NULL DEFAULT 0,
                    upgrade_accel INTEGER NOT NULL DEFAULT 0,
                    upgrade_handling INTEGER NOT NULL DEFAULT 0,
                    upgrade_nitro INTEGER NOT NULL DEFAULT 0,
                    upgrade_fuel_efficiency INTEGER NOT NULL DEFAULT 0
                )
            """)
            # Unlocked Cars
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unlocked_cars (
                    car_id TEXT PRIMARY KEY,
                    unlocked_at INTEGER NOT NULL
                )
            """)
            # Insert default career profile if empty
            cursor.execute("SELECT COUNT(*) FROM career_profile")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO career_profile (id, player_name, credits) VALUES (1, 'Racer 1', 500)")
                cursor.execute("INSERT OR IGNORE INTO unlocked_cars (car_id, unlocked_at) VALUES ('player_red', ?)", (int(time.time()),))
                cursor.execute("INSERT OR IGNORE INTO unlocked_cars (car_id, unlocked_at) VALUES ('player_cyan', ?)", (int(time.time()),))

            conn.commit()

    def add_high_score(self, player_name: str, score: int, distance: float, track_name: str, car_model: str) -> int:
        """Add a new high score entry."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO high_scores (player_name, score, distance, track_name, car_model, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (player_name, score, distance, track_name, car_model, int(time.time())))
            conn.commit()
            return cursor.lastrowid

    def get_top_scores(self, track_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve leaderboard high scores."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if track_name:
                cursor.execute("""
                    SELECT player_name, score, distance, track_name, car_model, timestamp
                    FROM high_scores
                    WHERE track_name = ?
                    ORDER BY score DESC LIMIT ?
                """, (track_name, limit))
            else:
                cursor.execute("""
                    SELECT player_name, score, distance, track_name, car_model, timestamp
                    FROM high_scores
                    ORDER BY score DESC LIMIT ?
                """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_career_profile(self) -> Dict[str, Any]:
        """Fetch career stats and upgrade levels."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM career_profile WHERE id = 1")
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {}

    def update_career_stats(self, added_credits: int, distance: float):
        """Update credits, total distance, and race count."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE career_profile
                SET credits = credits + ?,
                    total_distance = total_distance + ?,
                    total_races = total_races + 1
                WHERE id = 1
            """, (added_credits, distance))
            conn.commit()

    def purchase_upgrade(self, upgrade_type: str, cost: int) -> bool:
        """Upgrade vehicle stat if player has sufficient credits."""
        valid_types = {
            "top_speed": "upgrade_top_speed",
            "accel": "upgrade_accel",
            "handling": "upgrade_handling",
            "nitro": "upgrade_nitro",
            "fuel_efficiency": "upgrade_fuel_efficiency"
        }
        if upgrade_type not in valid_types:
            return False

        col_name = valid_types[upgrade_type]
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT credits, " + col_name + " FROM career_profile WHERE id = 1")
            row = cursor.fetchone()
            if not row:
                return False
            credits, curr_lvl = row[0], row[1]
            if credits < cost or curr_lvl >= 5:
                return False

            cursor.execute(f"""
                UPDATE career_profile
                SET credits = credits - ?,
                    {col_name} = {col_name} + 1
                WHERE id = 1
            """, (cost,))
            conn.commit()
            return True

    def select_car(self, car_id: str):
        """Set the active vehicle in career profile."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE career_profile SET selected_car = ? WHERE id = 1", (car_id,))
            conn.commit()

    def is_car_unlocked(self, car_id: str) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM unlocked_cars WHERE car_id = ?", (car_id,))
            return cursor.fetchone()[0] > 0

    def unlock_car(self, car_id: str, cost: int) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT credits FROM career_profile WHERE id = 1")
            credits = cursor.fetchone()[0]
            if credits < cost:
                return False
            cursor.execute("UPDATE career_profile SET credits = credits - ? WHERE id = 1", (cost,))
            cursor.execute("INSERT OR IGNORE INTO unlocked_cars (car_id, unlocked_at) VALUES (?, ?)", (car_id, int(time.time())))
            conn.commit()
            return True
