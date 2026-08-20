"""Dedicated Collision Module supporting Player, Enemy, Roadside, and Pickup Collisions."""

import math
from typing import List, Tuple, Optional
import pygame

from retro_racer.entities.player import PlayerCar
from retro_racer.entities.traffic import TrafficCar
from retro_racer.entities.roadside import RoadsideObject
from retro_racer.entities.pickups import Pickup, Hazard, HazardType
from retro_racer.config import CRASH_DAMAGE, SCRAPE_DAMAGE, COLOR_CYAN, COLOR_YELLOW, COLOR_GREEN


class CollisionSystem:
    """Detects and resolves overlaps between player, enemies, roadside objects, pickups, and hazards."""

    @staticmethod
    def process_player_traffic(player: PlayerCar, traffic_cars: List[TrafficCar],
                               audio_mgr, particle_system, camera, renderer) -> bool:
        """Process player collision with traffic vehicles. Returns True if full crash occurred."""
        player_hitbox = player.get_hitbox()
        crashed = False

        for traffic in traffic_cars:
            if traffic.is_crashed:
                continue

            traffic_hitbox = traffic.get_hitbox()

            # 1. Direct Collision
            if player_hitbox.colliderect(traffic_hitbox):
                # Shield Deflection
                if player.shield_timer > 0:
                    traffic.is_crashed = True
                    traffic.apply_oil_spin(1.5)
                    particle_system.spawn_explosion(traffic.position_x, traffic.position_y)
                    audio_mgr.play_sfx("crash")
                    camera.add_shake(6.0)
                    renderer.add_floating_text("SHIELD DEFLECT!", player.position_x, player.position_y - 20, COLOR_CYAN)
                    continue

                crashed = True
                impact_speed = abs(player.speed - traffic.speed)
                damage = CRASH_DAMAGE if impact_speed > 90.0 else SCRAPE_DAMAGE
                player.health = max(0.0, player.health - damage)
                traffic.health = max(0.0, traffic.health - damage)

                # Push physics response
                traffic.is_crashed = True
                traffic.speed = max(0.0, traffic.speed - 120.0)
                player.speed = max(40.0, player.speed * 0.45)

                # Lateral deflection recoil
                if player.position_x < traffic.position_x:
                    player.position_x -= 15.0
                    traffic.position_x += 15.0
                else:
                    player.position_x += 15.0
                    traffic.position_x -= 15.0

                # VFX & Audio
                mid_x = (player.position_x + traffic.position_x) / 2.0
                mid_y = (player.position_y + traffic.position_y) / 2.0
                particle_system.spawn_explosion(mid_x, mid_y)
                particle_system.spawn_sparks(mid_x, mid_y, count=14)
                audio_mgr.play_sfx("crash")
                camera.add_shake(12.0)

                if player.health <= 0:
                    player.is_crashed = True

                break

            # 2. Near-Miss Overtake Detection
            elif (traffic not in player.overtaken_cars) and (player.speed > traffic.speed + 30.0):
                near_miss_box = player.get_near_miss_hitbox(margin=16.0)
                if near_miss_box.colliderect(traffic_hitbox):
                    if player.position_y > traffic.position_y:
                        player.overtaken_cars.add(traffic)
                        pts = player.trigger_near_miss()
                        audio_mgr.play_sfx("near_miss", volume_scale=0.8)
                        combo_str = f" x{player.combo_count}" if player.combo_count > 1 else ""
                        renderer.add_floating_text(f"NEAR MISS! +{pts}{combo_str}", player.position_x, player.position_y - 18, COLOR_YELLOW)

        return crashed

    @staticmethod
    def process_player_roadside(player: PlayerCar, roadside_objects: List[RoadsideObject],
                                audio_mgr, particle_system, camera, renderer):
        """Process player collision with roadside props (trees, posts, rocks)."""
        player_hitbox = player.get_hitbox()
        for obj in roadside_objects:
            obj_box = obj.get_hitbox()
            if player_hitbox.colliderect(obj_box):
                if player.shield_timer > 0:
                    particle_system.spawn_sparks(obj.x, obj.y, count=8)
                    camera.add_shake(4.0)
                    continue

                player.health = max(0.0, player.health - CRASH_DAMAGE * 0.8)
                player.speed = max(20.0, player.speed * 0.3)
                particle_system.spawn_explosion(obj.x, obj.y)
                particle_system.spawn_sparks(obj.x, obj.y, count=12)
                audio_mgr.play_sfx("crash")
                camera.add_shake(10.0)
                renderer.add_floating_text("ROADSIDE CRASH!", player.position_x, player.position_y - 20, (255, 60, 60))

                if player.health <= 0:
                    player.is_crashed = True
                break

    @staticmethod
    def process_enemy_enemy(traffic_cars: List[TrafficCar], particle_system, audio_mgr):
        """Process collision between AI traffic vehicles."""
        n = len(traffic_cars)
        for i in range(n):
            for j in range(i + 1, n):
                c1 = traffic_cars[i]
                c2 = traffic_cars[j]
                if c1.is_crashed and c2.is_crashed:
                    continue

                if c1.get_hitbox().colliderect(c2.get_hitbox()):
                    # Deflect cars apart
                    c1.speed = max(40.0, c1.speed * 0.7)
                    c2.speed = max(40.0, c2.speed * 0.7)
                    if c1.position_x < c2.position_x:
                        c1.position_x -= 8.0
                        c2.position_x += 8.0
                    else:
                        c1.position_x += 8.0
                        c2.position_x -= 8.0
                    particle_system.spawn_sparks((c1.position_x + c2.position_x) / 2, (c1.position_y + c2.position_y) / 2, count=6)

    @staticmethod
    def process_pickups(player: PlayerCar, pickups: List[Pickup], audio_mgr, renderer):
        """Process item collection."""
        player_box = player.get_hitbox()
        for p in pickups:
            if not p.is_collected and player_box.colliderect(p.get_hitbox()):
                p.is_collected = True
                player.collect_pickup(p.pickup_type.value, p.amount)

                # Sound & Floating notification
                if p.pickup_type.value == "coin":
                    audio_mgr.play_sfx("coin")
                    renderer.add_floating_text(f"+{int(p.amount)} PTS", p.x, p.y - 12, COLOR_YELLOW)
                elif p.pickup_type.value == "fuel":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("+FUEL", p.x, p.y - 12, COLOR_GREEN)
                elif p.pickup_type.value == "nitro":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("+NITRO", p.x, p.y - 12, COLOR_CYAN)
                elif p.pickup_type.value == "shield":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("SHIELD ON!", p.x, p.y - 12, COLOR_CYAN)
                elif p.pickup_type.value == "magnet":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("MAGNET ON!", p.x, p.y - 12, COLOR_YELLOW)
                elif p.pickup_type.value == "slowmo":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("SLOW-MO!", p.x, p.y - 12, COLOR_CYAN)
                elif p.pickup_type.value == "2x":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("2X SCORE!", p.x, p.y - 12, COLOR_YELLOW)
                elif p.pickup_type.value == "wrench":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("+REPAIR", p.x, p.y - 12, COLOR_GREEN)

    @staticmethod
    def process_hazards(player: PlayerCar, hazards: List[Hazard], audio_mgr, particle_system, camera, renderer):
        """Process road hazards like oil slicks and cones."""
        player_box = player.get_hitbox()
        for h in hazards:
            if not h.is_hit and player_box.colliderect(h.get_hitbox()):
                h.is_hit = True
                if h.hazard_type == HazardType.OIL_SLICK:
                    player.apply_oil_spin(1.2)
                    audio_mgr.play_sfx("skid")
                    camera.add_shake(4.0)
                    renderer.add_floating_text("OIL SPIN!", player.position_x, player.position_y - 18, (255, 100, 100))
                elif h.hazard_type == HazardType.ROAD_CONE:
                    player.speed = max(30.0, player.speed - 30.0)
                    particle_system.spawn_sparks(h.x, h.y, count=5)
                    audio_mgr.play_sfx("skid", volume_scale=0.5)
                    camera.add_shake(2.0)
