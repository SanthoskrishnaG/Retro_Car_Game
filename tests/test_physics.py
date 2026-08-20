"""Unit tests for vehicle dynamics, acceleration, braking, and steering physics."""

import pytest
from retro_racer.entities.player import PlayerCar
from retro_racer.config import (
    ROAD_LEFT_EDGE, ROAD_RIGHT_EDGE, PLAYER_OFFROAD_MAX_SPEED, NITRO_MAX, FUEL_MAX
)


def test_player_car_initial_state():
    car = PlayerCar(240.0, 0.0)
    assert car.speed == 0.0
    assert car.fuel == FUEL_MAX
    assert car.health == 100.0
    assert not car.is_crashed
    assert not car.is_nitro_active


def test_player_acceleration_and_braking():
    car = PlayerCar(240.0, 0.0)
    dt = 0.1

    # Accelerate
    for _ in range(10):
        car.update_physics(
            dt=dt, steer_input=0.0, throttle=True, brake=False,
            nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
        )
    assert car.speed > 100.0
    initial_speed = car.speed

    # Brake
    for _ in range(10):
        car.update_physics(
            dt=dt, steer_input=0.0, throttle=False, brake=True,
            nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
        )
    assert car.speed < initial_speed


def test_player_steering_and_lateral_motion():
    car = PlayerCar(240.0, 0.0)
    car.speed = 200.0  # moving forward
    initial_x = car.x
    dt = 0.1

    # Steer right
    for _ in range(5):
        car.update_physics(
            dt=dt, steer_input=1.0, throttle=True, brake=False,
            nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
        )
    assert car.x > initial_x


def test_offroad_speed_penalty():
    car = PlayerCar(20.0, 0.0)  # Offroad position
    car.speed = 300.0
    dt = 0.1

    for _ in range(15):
        car.update_physics(
            dt=dt, steer_input=0.0, throttle=True, brake=False,
            nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
        )
    assert car.speed <= PLAYER_OFFROAD_MAX_SPEED + 1.0


def test_nitro_boost_activation():
    car = PlayerCar(240.0, 0.0)
    car.speed = 200.0
    car.nitro = 50.0
    dt = 0.1

    car.update_physics(
        dt=dt, steer_input=0.0, throttle=True, brake=False,
        nitro_req=True, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
    )
    assert car.is_nitro_active
    assert car.nitro < 50.0  # nitro consumed
