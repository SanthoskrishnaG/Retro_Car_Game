"""Game State Management and State Machine interface."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
import pygame


class State(ABC):
    """Base class for all game states."""

    def __init__(self, engine):
        self.engine = engine

    def on_enter(self, **kwargs):
        """Called when entering this state."""
        pass

    def on_exit(self):
        """Called when exiting this state."""
        pass

    @abstractmethod
    def handle_events(self, events: list):
        """Process frame events."""
        pass

    @abstractmethod
    def update(self, dt: float):
        """Update state logic."""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        """Draw state to virtual canvas."""
        pass


class StateManager:
    """Manages switching and stack transitions between game states."""

    def __init__(self):
        self.states: Dict[str, State] = {}
        self.current_state: Optional[State] = None
        self.current_state_name: str = ""
        self.state_stack: list = []

    def register_state(self, name: str, state: State):
        self.states[name] = state

    def change_state(self, name: str, **kwargs):
        """Switch current state with cleanup and initialize hooks."""
        if self.current_state:
            self.current_state.on_exit()
        if name in self.states:
            self.current_state_name = name
            self.current_state = self.states[name]
            self.current_state.on_enter(**kwargs)

    def push_state(self, name: str, **kwargs):
        """Push new state on top of stack (e.g. Pause modal)."""
        if self.current_state:
            self.state_stack.append((self.current_state_name, self.current_state))
        if name in self.states:
            self.current_state_name = name
            self.current_state = self.states[name]
            self.current_state.on_enter(**kwargs)

    def pop_state(self):
        """Pop top state and resume previous state."""
        if self.current_state:
            self.current_state.on_exit()
        if self.state_stack:
            self.current_state_name, self.current_state = self.state_stack.pop()
