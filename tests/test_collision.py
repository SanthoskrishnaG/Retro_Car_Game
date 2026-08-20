"""Unit tests for collision geometry, roadside crashes, enemy vs enemy, and near-miss detection."""

import pytest
import pygame
from retro_racer.entities.player import PlayerCar
from retro_racer.entities.traffic import TrafficCar, EnemyBehavior
from retro_racer.entities.roadside import RoadsideObject
from retro_racer.entities.pickups import Pickup, PickupType
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
    car = PlayerCar(160.0, 200.0)
    hitbox = car.get_hitbox()
    assert isinstance(hitbox, pygame.Rect)
    assert hitbox.centerx == 160
    assert hitbox.centery == 200


def test_direct_collision_detection():
    pygame.init()
    player = PlayerCar(160.0, 200.0)
    player.speed = 250.0
    traffic = TrafficCar(160.0, 200.0, EnemyBehavior.NORMAL)

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
    player = PlayerCar(160.0, 200.0)
    player.shield_timer = 5.0
    traffic = TrafficCar(160.0, 200.0, EnemyBehavior.NORMAL)

    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()
    renderer = DummyRenderer()

    crashed = CollisionSystem.process_player_traffic(
        player, [traffic], audio, particles, camera, renderer
    )
    assert not crashed
    assert player.health == 100.0
    assert traffic.is_crashed


def test_player_roadside_collision():
    pygame.init()
    player = PlayerCar(60.0, 200.0)
    player.speed = 200.0
    tree = RoadsideObject(60.0, 200.0, "scenery_oak_tree")

    audio = DummyAudio()
    particles = DummyParticles()
    camera = DummyCamera()
    renderer = DummyRenderer()

    CollisionSystem.process_player_roadside(
        player, [tree], audio, particles, camera, renderer
    )
    assert player.health < 100.0
    assert player.speed < 200.0


def test_enemy_enemy_collision():
    t1 = TrafficCar(160.0, 200.0, EnemyBehavior.NORMAL)
    t2 = TrafficCar(160.0, 200.0, EnemyBehavior.SLOW)
    particles = DummyParticles()
    audio = DummyAudio()

    CollisionSystem.process_enemy_enemy([t1, t2], particles, audio)
    # Positions deflected apart
    assert t1.position_x != t2.position_x


def test_player_pickup_collision():
    player = PlayerCar(160.0, 200.0)
    player.fuel = 40.0
    fuel_can = Pickup(160.0, 200.0, PickupType.FUEL)

    audio = DummyAudio()
    renderer = DummyRenderer()

    CollisionSystem.process_pickups(player, [fuel_can], audio, renderer)
    assert fuel_can.is_collected
    assert player.fuel > 40.0


def test_near_miss_detection():
    pygame.init()
    player = PlayerCar(160.0, 220.0)
    player.speed = 280.0
    traffic = TrafficCar(182.0, 200.0, EnemyBehavior.NORMAL)
    traffic.speed = 150.0

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
