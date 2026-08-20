"""Unit tests for collision geometry, hitbox math, and near-miss detection."""

import pytest
import pygame
from retro_racer.entities.player import PlayerCar
from retro_racer.entities.traffic import TrafficCar, TrafficType
from retro_racer.world.collision import CollisionSystem


class DummyAudio:
    def play_sfx(self, name, volume_scale=1.0):
        pass


class DummyParticles:
    def spawn_explosion(self, x, y):
        pass
    def spawn_sparks(self, x, y, count=8):
        pass


class DummyCamera:
    def add_shake(self, amount):
        pass


class DummyRenderer:
    def add_floating_text(self, text, x, y, color=None):
        pass


def test_car_hitbox_generation():
    car = PlayerCar(200.0, 300.0)
    hitbox = car.get_hitbox()
    assert isinstance(hitbox, pygame.Rect)
    assert hitbox.centerx == 200
    assert hitbox.centery == 300


def test_direct_collision_detection():
    pygame.init()
    player = PlayerCar(200.0, 300.0)
    player.speed = 300.0
    traffic = TrafficCar(200.0, 300.0, TrafficType.SEDAN)

    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()
    renderer = DummyRenderer()

    crashed = CollisionSystem.process_player_traffic(
        player, [traffic], audio, particles, camera, renderer
    )
    assert crashed
    assert traffic.is_crashed
    assert player.health < 100.0


def test_shield_collision_protection():
    pygame.init()
    player = PlayerCar(200.0, 300.0)
    player.shield_timer = 5.0
    traffic = TrafficCar(200.0, 300.0, TrafficType.SEDAN)

    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()
    renderer = DummyRenderer()

    crashed = CollisionSystem.process_player_traffic(
        player, [traffic], audio, particles, camera, renderer
    )
    assert not crashed
    assert player.health == 100.0  # unharmed
    assert traffic.is_crashed      # deflected


def test_near_miss_detection():
    pygame.init()
    player = PlayerCar(200.0, 320.0)
    player.speed = 350.0
    traffic = TrafficCar(228.0, 300.0, TrafficType.SEDAN)  # close lane, slightly behind
    traffic.speed = 200.0

    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()
    renderer = DummyRenderer()

    initial_score = player.score
    CollisionSystem.process_player_traffic(
        player, [traffic], audio, particles, camera, renderer
    )
    assert player.score > initial_score
    assert player.combo_count >= 1
