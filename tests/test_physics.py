"""Unit tests for vehicle dynamics, properties, acceleration, braking, and delta-time integration."""

import pytest
from retro_racer.entities.player import PlayerCar
from retro_racer.config import (
    ROAD_LEFT_EDGE, ROAD_RIGHT_EDGE, PLAYER_OFFROAD_MAX_SPEED, NITRO_MAX, FUEL_MAX
)


def test_player_vehicle_model_properties():
    car = PlayerCar(160.0, 50.0)
    # Validate exact properties requested in specifications
    assert hasattr(car, "position_x")
    assert hasattr(car, "position_y")
    assert hasattr(car, "velocity_x")
    assert hasattr(car, "velocity_y")
    assert hasattr(car, "speed")
    assert hasattr(car, "max_speed")
    assert hasattr(car, "acceleration")
    assert hasattr(car, "braking_force")
    assert hasattr(car, "friction")
    assert hasattr(car, "steering_speed")
    assert hasattr(car, "fuel")
    assert hasattr(car, "nitro")
    assert hasattr(car, "health")
    assert hasattr(car, "score")

    assert car.position_x == 160.0
    assert car.position_y == 50.0
    assert car.fuel == FUEL_MAX
    assert car.health == 100.0
    assert not car.is_crashed


def test_player_acceleration_and_braking():
    car = PlayerCar(160.0, 0.0)
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
    car = PlayerCar(160.0, 0.0)
    car.speed = 200.0
    initial_x = car.position_x
    dt = 0.1

    # Steer right
    for _ in range(5):
        car.update_physics(
            dt=dt, steer_input=1.0, throttle=True, brake=False,
            nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
        )
    assert car.position_x > initial_x
    assert car.velocity_x > 0.0


def test_delta_time_step_stability():
    # Test 60 FPS (dt=0.0166) vs 30 FPS (dt=0.0333) integration
    car_60 = PlayerCar(160.0, 0.0)
    car_30 = PlayerCar(160.0, 0.0)

    # 1 second of acceleration
    for _ in range(60):
        car_60.update_physics(dt=1.0 / 60.0, steer_input=0.0, throttle=True, brake=False, nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE)

    for _ in range(30):
        car_30.update_physics(dt=1.0 / 30.0, steer_input=0.0, throttle=True, brake=False, nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE)

    # Both vehicles should reach comparable speeds and positions
    assert abs(car_60.speed - car_30.speed) < 15.0
    assert abs(car_60.position_y - car_30.position_y) < 25.0


def test_offroad_speed_penalty():
    car = PlayerCar(10.0, 0.0)  # Offroad position
    car.speed = 300.0
    dt = 0.1

    for _ in range(15):
        car.update_physics(
            dt=dt, steer_input=0.0, throttle=True, brake=False,
            nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
        )
    assert car.speed <= PLAYER_OFFROAD_MAX_SPEED + 1.0


def test_nitro_boost_activation():
    car = PlayerCar(160.0, 0.0)
    car.speed = 200.0
    car.nitro = 50.0
    dt = 0.1

    car.update_physics(
        dt=dt, steer_input=0.0, throttle=True, brake=False,
        nitro_req=True, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
    )
    assert car.is_nitro_active
    assert car.nitro < 50.0


def test_crash_state_behavior():
    car = PlayerCar(160.0, 0.0)
    car.speed = 250.0
    car.is_crashed = True
    dt = 0.1

    car.update_physics(
        dt=dt, steer_input=1.0, throttle=True, brake=False,
        nitro_req=False, road_left=ROAD_LEFT_EDGE, road_right=ROAD_RIGHT_EDGE
    )
    # In crash state, throttle is ignored and speed rapidly decelerates
    assert car.speed < 250.0
    assert car.spin_timer >= 0.0
