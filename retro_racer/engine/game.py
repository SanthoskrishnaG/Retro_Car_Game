"""Main Game Engine and application loop coordinator."""

import sys
import pygame

from retro_racer.config import (
    GAME_TITLE, VIRTUAL_WIDTH, VIRTUAL_HEIGHT, DEFAULT_SCALE,
    TARGET_FPS
)
from retro_racer.systems.asset_pipeline import AssetPipeline
from retro_racer.systems.database import Database
from retro_racer.systems.replay import ReplayManager
from retro_racer.systems.level_editor import LevelEditor
from retro_racer.systems.debug import DebugOverlay

from retro_racer.engine.audio import AudioManager
from retro_racer.engine.input_handler import InputHandler
from retro_racer.engine.renderer import Renderer
from retro_racer.engine.state_manager import StateManager

from retro_racer.states.title_state import TitleState
from retro_racer.states.play_state import PlayState
from retro_racer.states.garage_state import GarageState
from retro_racer.states.leaderboard_state import LeaderboardState
from retro_racer.states.editor_state import EditorState
from retro_racer.states.replay_state import ReplayState
from retro_racer.states.settings_state import SettingsState
from retro_racer.states.game_over_state import GameOverState


class GameEngine:
    """Core Game Engine orchestrating window scaling, state machine, and main loop."""

    def __init__(self, scale: float = DEFAULT_SCALE, headless: bool = False):
        self.scale = scale
        self.is_fullscreen = False
        self.headless = headless
        self.running = False
        self.clock = pygame.time.Clock()
        self.dt = 0.016

        # Initialize Subsystems
        self.asset_pipeline = AssetPipeline()
        self.db = Database()
        self.replay_mgr = ReplayManager()
        self.level_editor = LevelEditor()
        self.debug = DebugOverlay()

        # Window & Display
        self.window_w = int(VIRTUAL_WIDTH * scale)
        self.window_h = int(VIRTUAL_HEIGHT * scale)
        self.screen = None

        if not headless:
            pygame.init()
            pygame.display.set_caption(GAME_TITLE)
            self.screen = pygame.display.set_mode((self.window_w, self.window_h), pygame.DOUBLEBUF | pygame.RESIZABLE)

        self.audio_mgr = AudioManager()
        self.input_handler = InputHandler()
        self.renderer = Renderer(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        self.state_mgr = StateManager()

        # Generate sprites
        self.asset_pipeline.generate_all_sprites()

        # Register States
        self._register_states()

    def set_display_scale(self, scale: float):
        """Set window resolution scaling multiple (1x, 2x, 3x, 4x)."""
        self.scale = scale
        self.is_fullscreen = False
        self.window_w = int(VIRTUAL_WIDTH * scale)
        self.window_h = int(VIRTUAL_HEIGHT * scale)
        if self.screen and not self.headless:
            self.screen = pygame.display.set_mode((self.window_w, self.window_h), pygame.DOUBLEBUF | pygame.RESIZABLE)

    def toggle_fullscreen(self):
        """Toggle Fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        if self.screen and not self.headless:
            if self.is_fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            else:
                self.screen = pygame.display.set_mode((self.window_w, self.window_h), pygame.DOUBLEBUF | pygame.RESIZABLE)

    def _register_states(self):
        self.state_mgr.register_state("title", TitleState(self))
        self.state_mgr.register_state("play", PlayState(self))
        self.state_mgr.register_state("garage", GarageState(self))
        self.state_mgr.register_state("leaderboard", LeaderboardState(self))
        self.state_mgr.register_state("editor", EditorState(self))
        self.state_mgr.register_state("replay", ReplayState(self))
        self.state_mgr.register_state("settings", SettingsState(self))
        self.state_mgr.register_state("game_over", GameOverState(self))

    def run(self, initial_state: str = "title", **kwargs):
        """Start the game loop."""
        self.running = True
        self.state_mgr.change_state(initial_state, **kwargs)

        while self.running:
            # 1. Delta Time
            self.dt = min(0.05, self.clock.tick(TARGET_FPS) / 1000.0)

            # 2. Event Handling
            self.input_handler.begin_frame()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    if not self.is_fullscreen and not self.headless:
                        self.screen = pygame.display.set_mode(event.size, pygame.DOUBLEBUF | pygame.RESIZABLE)
                self.input_handler.process_event(event, scale=self.scale)

            self.input_handler.update_continuous_actions()

            # Global Hotkeys
            if self.input_handler.is_action_just_pressed("fullscreen"):
                self.toggle_fullscreen()
            elif self.input_handler.is_action_just_pressed("mute"):
                self.audio_mgr.toggle_mute()

            if self.state_mgr.current_state:
                self.state_mgr.current_state.handle_events(events)

            # 3. State Update
            if self.state_mgr.current_state:
                self.state_mgr.current_state.update(self.dt)

            # 4. Rendering
            if self.screen and self.state_mgr.current_state:
                self.state_mgr.current_state.render(self.renderer.virtual_surface)
                self.renderer.render_to_screen(self.screen)
                pygame.display.flip()

        self._shutdown()

    def _shutdown(self):
        self.audio_mgr.stop_music()
        self.audio_mgr.stop_engine()
        pygame.quit()
