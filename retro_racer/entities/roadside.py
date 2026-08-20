"""Roadside scenery props, trees, buildings, and trackside decorations."""

from typing import Optional
import pygame


class RoadsideObject:
    """Scenery object placed along the left or right shoulders of the highway."""

    def __init__(self, x: float, y: float, sprite_name: str, side: str = "left"):
        self.x = float(x)
        self.y = float(y)
        self.sprite_name = sprite_name
        self.side = side
        self.width = 48
        self.height = 56

    def render(self, surface: pygame.Surface, camera, asset_pipeline):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sy < -100 or sy > camera.height + 100:
            return

        sprite = asset_pipeline.get_surface(self.sprite_name, pygame)
        if sprite:
            w, h = sprite.get_size()
            surface.blit(sprite, (sx - w // 2, sy - h // 2))
        else:
            # Fallback simple tree representation
            pygame.draw.circle(surface, (30, 150, 60), (sx, sy), 18)
