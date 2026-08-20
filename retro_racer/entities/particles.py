"""Particle Effects Engine: Explosions, Skid Marks, Nitro Jet Flames, and Sparks."""

import random
import math
from typing import List, Tuple
import pygame

from retro_racer.config import COLOR_YELLOW, COLOR_RED, COLOR_CYAN, COLOR_WHITE


class Particle:
    """Individual visual effect particle."""

    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int],
                 size: float, lifetime: float, ptype: str = "generic"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_lifetime = lifetime
        self.life = lifetime
        self.ptype = ptype
        self.frame_idx = 0

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.ptype == "explosion":
            # 8 frames of animation
            progress = 1.0 - max(0.0, self.life / self.max_lifetime)
            self.frame_idx = min(7, int(progress * 8))
        return self.life > 0


class SkidMark:
    """Persistent tire skid mark left on the road surface."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.life = 6.0  # seconds before fade

    def update(self, dt: float) -> bool:
        self.life -= dt
        return self.life > 0


class ParticleSystem:
    """Manages all active particles, sparks, smoke, and explosions."""

    def __init__(self):
        self.particles: List[Particle] = []
        self.skid_marks: List[SkidMark] = []

    def clear(self):
        self.particles.clear()
        self.skid_marks.clear()

    def spawn_explosion(self, x: float, y: float):
        """Spawn big animated fireball explosion."""
        p = Particle(x, y, 0, 0, (255, 200, 50), size=48, lifetime=0.55, ptype="explosion")
        self.particles.append(p)
        # Accompanying flying spark debris
        self.spawn_sparks(x, y, count=24, speed_range=(120, 320))

    def spawn_sparks(self, x: float, y: float, count: int = 8, speed_range: Tuple[float, float] = (50, 180)):
        """Spawn metallic scrape collision sparks."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            col = random.choice([(255, 240, 100), (255, 180, 40), (255, 255, 255), (255, 100, 30)])
            p = Particle(x, y, vx, vy, col, size=random.uniform(2, 4), lifetime=random.uniform(0.2, 0.45), ptype="spark")
            self.particles.append(p)

    def spawn_nitro_flame(self, x: float, y: float):
        """Spawn nitro jet exhaust flame particles."""
        for _ in range(3):
            vx = random.uniform(-15, 15)
            vy = random.uniform(80, 160)
            col = random.choice([(0, 220, 255), (0, 140, 255), (200, 250, 255), (255, 255, 255)])
            p = Particle(x + random.uniform(-6, 6), y, vx, vy, col, size=random.uniform(3, 7), lifetime=0.18, ptype="nitro")
            self.particles.append(p)

    def spawn_smoke(self, x: float, y: float):
        """Spawn soft tire/engine exhaust smoke."""
        vx = random.uniform(-20, 20)
        vy = random.uniform(40, 80)
        col = (200, 205, 215)
        p = Particle(x, y, vx, vy, col, size=random.uniform(4, 9), lifetime=0.35, ptype="smoke")
        self.particles.append(p)

    def spawn_skid(self, x: float, y: float):
        """Spawn tire skid mark segment on the asphalt."""
        self.skid_marks.append(SkidMark(x, y))
        if len(self.skid_marks) > 200:
            self.skid_marks.pop(0)

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.skid_marks = [sm for sm in self.skid_marks if sm.update(dt)]

    def render_skids(self, surface: pygame.Surface, camera):
        """Render tire skid marks on asphalt layer."""
        for sm in self.skid_marks:
            sx, sy = camera.world_to_screen(sm.x, sm.y)
            if -20 < sy < camera.height + 20:
                alpha = int(140 * (sm.life / 6.0))
                skid_surf = pygame.Surface((4, 10), pygame.SRCALPHA)
                skid_surf.fill((25, 28, 35, alpha))
                surface.blit(skid_surf, (sx - 2, sy - 5))

    def render_particles(self, surface: pygame.Surface, camera, asset_pipeline):
        """Render all active particle types."""
        explosion_strip = asset_pipeline.get_surface("fx_explosion", pygame)

        for p in self.particles:
            sx, sy = camera.world_to_screen(p.x, p.y)
            if sy < -50 or sy > camera.height + 50:
                continue

            if p.ptype == "explosion" and explosion_strip:
                frame_w = 48
                frame_rect = pygame.Rect(p.frame_idx * frame_w, 0, frame_w, 48)
                surface.blit(explosion_strip, (sx - 24, sy - 24), frame_rect)
            elif p.ptype == "spark":
                pygame.draw.circle(surface, p.color, (sx, sy), int(p.size))
            elif p.ptype == "nitro":
                pygame.draw.circle(surface, p.color, (sx, sy), int(p.size))
            elif p.ptype == "smoke":
                alpha = int(180 * (p.life / p.max_lifetime))
                s_surf = pygame.Surface((int(p.size * 2), int(p.size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(s_surf, (*p.color[:3], alpha), (int(p.size), int(p.size)), int(p.size))
                surface.blit(s_surf, (sx - int(p.size), sy - int(p.size)))
