"""Retro Racer Python - Entry Point Script.

Run locally with:
    python main.py
"""

import argparse
import sys
from retro_racer.engine.game import GameEngine


def parse_args():
    parser = argparse.ArgumentParser(description="Retro Racer Python - 16-bit Pixel-Art Arcade Racing Engine")
    parser.add_argument("--scale", type=float, default=1.5, help="Window display scaling factor (default: 1.5)")
    parser.add_argument("--state", type=str, default="title", choices=["title", "play", "garage", "editor", "replay", "leaderboard", "settings"], help="Initial state to launch")
    parser.add_argument("--mute", action="store_true", help="Start game with sound muted")
    parser.add_argument("--track", type=str, default=None, help="Custom track JSON name to load directly")
    return parser.parse_args()


def main():
    args = parse_args()

    engine = GameEngine(scale=args.scale)
    if args.mute:
        engine.audio_mgr.toggle_mute()

    kwargs = {}
    if args.track:
        track = engine.level_editor.load_track(args.track)
        if track:
            kwargs["track_data"] = track

    engine.run(initial_state=args.state, **kwargs)


if __name__ == "__main__":
    main()
