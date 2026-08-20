"""Replay Recording, Serialization, and Playback System."""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from retro_racer.config import REPLAYS_DIR


class ReplayManager:
    """Handles recording gameplay frames and playing them back."""

    def __init__(self, replays_dir: Path = REPLAYS_DIR):
        self.replays_dir = replays_dir
        self.replays_dir.mkdir(parents=True, exist_ok=True)
        self.is_recording = False
        self.is_playing = False
        self.current_frame = 0
        self.playback_speed = 1.0
        self.frames: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    def start_recording(self, track_name: str, car_model: str, player_name: str):
        """Begin a new recording session."""
        self.frames.clear()
        self.is_recording = True
        self.is_playing = False
        self.metadata = {
            "track_name": track_name,
            "car_model": car_model,
            "player_name": player_name,
            "start_time": int(time.time()),
            "total_frames": 0,
            "final_score": 0,
            "final_distance": 0.0
        }

    def record_frame(self, frame_data: Dict[str, Any]):
        """Capture one tick of gameplay state."""
        if not self.is_recording:
            return
        self.frames.append(frame_data)

    def stop_recording(self, final_score: int, final_distance: float) -> Optional[Path]:
        """Finish recording and persist replay to a JSON file."""
        if not self.is_recording:
            return None
        self.is_recording = False
        self.metadata["total_frames"] = len(self.frames)
        self.metadata["final_score"] = final_score
        self.metadata["final_distance"] = round(final_distance, 1)

        filename = f"replay_{self.metadata['start_time']}_{final_score}pts.json"
        filepath = self.replays_dir / filename
        data = {
            "metadata": self.metadata,
            "frames": self.frames
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return filepath

    def load_replay(self, filepath: Path) -> bool:
        """Load a replay JSON file for playback."""
        if not filepath.exists():
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.metadata = data.get("metadata", {})
            self.frames = data.get("frames", [])
            self.current_frame = 0
            self.is_playing = True
            self.is_recording = False
            return True
        except Exception:
            return False

    def list_saved_replays(self) -> List[Path]:
        """Return list of saved replay files sorted by newest first."""
        return sorted(self.replays_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    def get_current_frame_data(self) -> Optional[Dict[str, Any]]:
        """Get state dictionary for the current playback frame."""
        if not self.frames or self.current_frame >= len(self.frames):
            return None
        return self.frames[self.current_frame]

    def advance_playback(self, dt: float) -> bool:
        """Advance replay timeline based on playback speed and delta time."""
        if not self.is_playing or not self.frames:
            return False
        # 60 FPS standard replay rate
        frames_to_advance = max(1, int(60 * dt * self.playback_speed))
        self.current_frame += frames_to_advance
        if self.current_frame >= len(self.frames):
            self.current_frame = len(self.frames) - 1
            return False  # Finished
        return True

    def seek(self, frame_idx: int):
        """Jump to specific frame in replay."""
        if not self.frames:
            return
        self.current_frame = max(0, min(len(self.frames) - 1, frame_idx))
