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
    """Core Game Engine orchestrating window, subsystems, state machine, and main loop."""

    def __init__(self, scale: float = DEFAULT_SCALE, headless: bool = False):
        self.scale = scale
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
            self.screen = pygame.display.set_mode((self.window_w, self.window_h), pygame.DOUBLEBUF)

        self.audio_mgr = AudioManager()
        self.input_handler = InputHandler()
        self.renderer = Renderer(VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        self.state_mgr = StateManager()

        # Generate sprites
        self.asset_pipeline.generate_all_sprites()

        # Register States
        self._register_states()

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
                self.input_handler.process_event(event, scale=self.scale)

            self.input_handler.update_continuous_actions()

            if self.state_mgr.current_state:
                self.state_mgr.current_state.handle_events(events)

            # 3. State Update
            if self.state_mgr.current_state:
                self.state_mgr.current_state.update(self.dt)

            # 4. Rendering
            if self.screen and self.state_mgr.current_state:
                # Render state to virtual pixel canvas
                self.state_mgr.current_state.render(self.renderer.virtual_surface)
                # Scale up to screen with CRT scanlines post-processing
                self.renderer.render_to_screen(self.screen)
                pygame.display.flip()

        self._shutdown()

    def _shutdown(self):
        self.audio_mgr.stop_music()
        self.audio_mgr.stop_engine()
        pygame.quit()
