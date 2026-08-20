"""Global configuration, constants, and settings for Retro Racer Python."""

import os
from pathlib import Path
import pygame

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"
TRACKS_DIR = ASSETS_DIR / "tracks"
REPLAYS_DIR = BASE_DIR / "replays"
SAVES_DIR = BASE_DIR / "saves"
DB_PATH = SAVES_DIR / "retro_racer.db"
KEYBINDINGS_FILE = SAVES_DIR / "keybindings.json"

# Ensure directories exist
for directory in [ASSETS_DIR, SPRITES_DIR, TRACKS_DIR, REPLAYS_DIR, SAVES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Display & Window (Logical Retro Resolution: 320x240)
GAME_TITLE = "RETRO RACER PYTHON"
VIRTUAL_WIDTH = 320       # Logical retro width (sharp pixel art canvas)
VIRTUAL_HEIGHT = 240      # Logical retro height (sharp pixel art canvas)
DEFAULT_SCALE = 3.0       # Default window scaling factor (960x720 window)
TARGET_FPS = 60

# Palette - Curated 80s Arcade & Synthwave
COLOR_BLACK = (10, 10, 15)
COLOR_DARK_GRAY = (35, 38, 48)
COLOR_ASPHALT = (55, 60, 72)
COLOR_ROAD_EDGE = (75, 82, 98)
COLOR_WHITE = (245, 245, 250)
COLOR_YELLOW = (255, 204, 0)
COLOR_RED = (235, 50, 50)
COLOR_CRIMSON = (180, 20, 40)
COLOR_GREEN = (40, 190, 80)
COLOR_DARK_GREEN = (20, 110, 45)
COLOR_CYAN = (0, 220, 255)
COLOR_NEON_BLUE = (30, 144, 255)
COLOR_PURPLE = (168, 50, 220)
COLOR_MAGENTA = (255, 40, 140)
COLOR_ORANGE = (255, 128, 0)
COLOR_GOLD = (255, 215, 0)
COLOR_SAND = (222, 190, 130)
COLOR_DARK_SAND = (180, 145, 90)

# Road Dimensions (scaled for 320-wide canvas)
ROAD_LANES = 4
LANE_WIDTH = 46
ROAD_WIDTH = ROAD_LANES * LANE_WIDTH  # 184 px
ROAD_CENTER_X = VIRTUAL_WIDTH // 2    # 160 px
ROAD_LEFT_EDGE = ROAD_CENTER_X - ROAD_WIDTH // 2   # 68 px
ROAD_RIGHT_EDGE = ROAD_CENTER_X + ROAD_WIDTH // 2  # 252 px
STRIPE_LENGTH = 32
STRIPE_GAP = 24
CURB_WIDTH = 8

# Player Vehicle Physics Defaults
PLAYER_BASE_MAX_SPEED = 380.0     # px/s
PLAYER_ACCELERATION = 220.0       # px/s^2
PLAYER_BRAKING_FORCE = 380.0      # px/s^2
PLAYER_FRICTION = 90.0            # px/s^2 natural coasting deceleration
PLAYER_STEERING_SPEED = 240.0     # lateral px/s
PLAYER_DRIFT_FACTOR = 0.86        # steering inertia retention
PLAYER_OFFROAD_DECEL = 320.0      # penalty when driving on grass/dirt
PLAYER_OFFROAD_MAX_SPEED = 140.0  # max speed on grass

# Nitro Boost
NITRO_MAX = 100.0
NITRO_DEPLETION_RATE = 32.0       # units per second
NITRO_SPEED_MULTIPLIER = 1.45
NITRO_RECHARGE_RATE = 4.0         # passive refill per sec

# Fuel System
FUEL_MAX = 100.0
FUEL_DEPLETION_BASE = 2.0         # per second base
FUEL_DEPLETION_SPEED_SCALE = 0.008# additional consumption with high speed
FUEL_PICKUP_AMOUNT = 35.0

# Health & Combat
PLAYER_MAX_HEALTH = 100.0
CRASH_DAMAGE = 35.0
SCRAPE_DAMAGE = 10.0
SHIELD_DURATION = 8.0             # seconds
MAGNET_DURATION = 10.0
SLOW_MO_DURATION = 6.0
SLOW_MO_FACTOR = 0.45
DOUBLE_SCORE_DURATION = 12.0

# Scoring
SCORE_PER_METER = 2
NEAR_MISS_BASE_SCORE = 150
NEAR_MISS_DISTANCE = 24.0         # px threshold for near miss
OVERTAKE_SCORE = 50
COIN_SCORE = 200

# Spawning & Traffic
TRAFFIC_SPAWN_INTERVAL_MIN = 0.8  # seconds
TRAFFIC_SPAWN_INTERVAL_MAX = 2.2
MAX_CONCURRENT_TRAFFIC = 8
MIN_TRAFFIC_SPEED = 140.0
MAX_TRAFFIC_SPEED = 300.0

# Audio
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2
MASTER_VOLUME = 0.8
SFX_VOLUME = 0.85
MUSIC_VOLUME = 0.65

# Biomes
BIOME_CITY_DAY = "city_day"
BIOME_CITY_NIGHT = "city_night"
BIOME_SYNTHWAVE = "synthwave"
BIOME_DESERT = "desert"
BIOME_ALPINE = "alpine"

# Default Key Bindings mapping action -> list of pygame key codes
DEFAULT_KEYBINDINGS = {
    "accelerate": [pygame.K_UP, pygame.K_w],
    "brake": [pygame.K_DOWN, pygame.K_s],
    "steer_left": [pygame.K_LEFT, pygame.K_a],
    "steer_right": [pygame.K_RIGHT, pygame.K_d],
    "nitro": [pygame.K_SPACE, pygame.K_LSHIFT],
    "pause": [pygame.K_ESCAPE, pygame.K_p],
    "confirm": [pygame.K_RETURN, pygame.K_SPACE],
    "restart": [pygame.K_r],
    "mute": [pygame.K_m],
    "fullscreen": [pygame.K_F11],
    "debug": [pygame.K_F3],
}
