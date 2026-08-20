"""Unit tests for PowerUp hierarchy, fuel depletion, and scoring systems."""

import pytest
import pygame
from retro_racer.entities.player import PlayerCar
from retro_racer.entities.pickups import (
    PowerUp, FuelPowerUp, NitroPowerUp, CoinPowerUp, ShieldPowerUp,
    RepairPowerUp, MagnetPowerUp, SlowMoPowerUp, MultiplierPowerUp,
    create_powerup, PickupType
)
from retro_racer.config import FUEL_MAX, NITRO_MAX


def test_powerup_base_class_and_subclasses():
    pygame.init()
    player = PlayerCar(160.0, 200.0)

    # 1. Fuel
    player.fuel = 20.0
    fuel_pu = FuelPowerUp(160.0, 200.0, amount=40.0)
    assert isinstance(fuel_pu, PowerUp)
    msg, sfx, col = fuel_pu.apply(player)
    assert player.fuel == 60.0
    assert "+FUEL" in msg

    # 2. Nitro
    player.nitro = 10.0
    nitro_pu = NitroPowerUp(160.0, 200.0, amount=50.0)
    assert isinstance(nitro_pu, PowerUp)
    msg, sfx, col = nitro_pu.apply(player)
    assert player.nitro == 60.0

    # 3. Coin
    player.score = 0
    coin_pu = CoinPowerUp(160.0, 200.0, amount=50)
    assert isinstance(coin_pu, PowerUp)
    coin_pu.apply(player)
    assert player.score == 50

    # 4. Shield
    player.shield_timer = 0.0
    shield_pu = ShieldPowerUp(160.0, 200.0, duration=6.0)
    assert isinstance(shield_pu, PowerUp)
    shield_pu.apply(player)
    assert player.shield_timer == 6.0

    # 5. Repair
    player.health = 50.0
    repair_pu = RepairPowerUp(160.0, 200.0, amount=30.0)
    assert isinstance(repair_pu, PowerUp)
    repair_pu.apply(player)
    assert player.health == 80.0


def test_factory_powerup_creation():
    pu = create_powerup(PickupType.SHIELD, 100.0, 200.0)
    assert isinstance(pu, ShieldPowerUp)
    assert pu.x == 100.0
    assert pu.y == 200.0


def test_zero_fuel_coasting_and_lockout():
    player = PlayerCar(160.0, 200.0)
    player.fuel = 0.0
    player.speed = 150.0

    # Try accelerating with no fuel
    player.update_physics(dt=0.1, steer_input=0.0, throttle=True, brake=False,
                          nitro_req=False, road_left=50.0, road_right=270.0)

    # Car must slow down, throttle must be ignored
    assert player.speed < 150.0
    assert player.out_of_fuel_timer > 0.0


def test_score_system_and_combos():
    player = PlayerCar(160.0, 200.0)
    player.score = 0

    # 1. Overtake (+100)
    pts_ot = player.trigger_overtake(100)
    assert pts_ot == 100
    assert player.score == 100
    assert player.combo_count == 1

    # 2. Near Miss (+250 base + combo bonus)
    pts_nm = player.trigger_near_miss(250)
    assert pts_nm > 250
    assert player.combo_count == 2

    # 3. Checkpoint (+1000)
    pts_cp = player.trigger_checkpoint(1500.0, base_score=1000)
    assert pts_cp == 1000
    assert player.score == 100 + pts_nm + 1000
    assert 1500.0 in player.cleared_checkpoints
