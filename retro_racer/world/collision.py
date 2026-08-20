"""Collision Detection, Near-Miss Triggering, and Physics Responses."""

import math
from typing import List, Tuple, Optional
import pygame

from retro_racer.entities.player import PlayerCar
from retro_racer.entities.traffic import TrafficCar
from retro_racer.entities.pickups import Pickup, Hazard, HazardType
from retro_racer.config import CRASH_DAMAGE, SCRAPE_DAMAGE, COLOR_CYAN, COLOR_YELLOW, COLOR_GREEN


class CollisionSystem:
    """Detects and resolves overlaps between player, traffic AI, pickups, and hazards."""

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
                # Check Shield Protection
                if player.shield_timer > 0:
                    traffic.is_crashed = True
                    traffic.apply_oil_spin(1.5)
                    particle_system.spawn_explosion(traffic.x, traffic.y)
                    audio_mgr.play_sfx("crash")
                    camera.add_shake(8.0)
                    renderer.add_floating_text("SHIELD DEFLECT!", player.x, player.y - 30, COLOR_CYAN)
                    continue

                # Normal Crash / Impact
                crashed = True
                impact_speed = abs(player.speed - traffic.speed)
                damage = CRASH_DAMAGE if impact_speed > 120.0 else SCRAPE_DAMAGE
                player.health = max(0.0, player.health - damage)

                # Push physics response
                traffic.is_crashed = True
                traffic.speed = max(0.0, traffic.speed - 150.0)
                player.speed = max(60.0, player.speed * 0.4)

                # Lateral deflection
                if player.x < traffic.x:
                    player.x -= 20.0
                    traffic.x += 20.0
                else:
                    player.x += 20.0
                    traffic.x -= 20.0

                # VFX & Audio
                mid_x = (player.x + traffic.x) / 2.0
                mid_y = (player.y + traffic.y) / 2.0
                particle_system.spawn_explosion(mid_x, mid_y)
                particle_system.spawn_sparks(mid_x, mid_y, count=16)
                audio_mgr.play_sfx("crash")
                camera.add_shake(16.0)

                if player.health <= 0:
                    player.is_crashed = True

                break

            # 2. Near-Miss Overtake Detection
            elif (traffic not in player.overtaken_cars) and (player.speed > traffic.speed + 40.0):
                near_miss_box = player.get_near_miss_hitbox(margin=20.0)
                if near_miss_box.colliderect(traffic_hitbox):
                    # Check if player has passed the front of the traffic vehicle
                    if player.y > traffic.y:
                        player.overtaken_cars.add(traffic)
                        pts = player.trigger_near_miss()
                        audio_mgr.play_sfx("near_miss", volume_scale=0.8)
                        combo_str = f" x{player.combo_count}" if player.combo_count > 1 else ""
                        renderer.add_floating_text(f"NEAR MISS! +{pts}{combo_str}", player.x, player.y - 25, COLOR_YELLOW)

        return crashed

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
                    renderer.add_floating_text(f"+{int(p.amount)} PTS", p.x, p.y - 15, COLOR_YELLOW)
                elif p.pickup_type.value == "fuel":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("+FUEL", p.x, p.y - 15, COLOR_GREEN)
                elif p.pickup_type.value == "nitro":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("+NITRO", p.x, p.y - 15, COLOR_CYAN)
                elif p.pickup_type.value == "shield":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("SHIELD ON!", p.x, p.y - 15, COLOR_CYAN)
                elif p.pickup_type.value == "magnet":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("MAGNET ON!", p.x, p.y - 15, COLOR_YELLOW)
                elif p.pickup_type.value == "slowmo":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("SLOW-MO!", p.x, p.y - 15, COLOR_CYAN)
                elif p.pickup_type.value == "2x":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("2X SCORE!", p.x, p.y - 15, COLOR_YELLOW)
                elif p.pickup_type.value == "wrench":
                    audio_mgr.play_sfx("pickup")
                    renderer.add_floating_text("+REPAIR", p.x, p.y - 15, COLOR_GREEN)

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
                    camera.add_shake(6.0)
                    renderer.add_floating_text("OIL SPIN!", player.x, player.y - 25, (255, 100, 100))
                elif h.hazard_type == HazardType.ROAD_CONE:
                    player.speed = max(40.0, player.speed - 40.0)
                    particle_system.spawn_sparks(h.x, h.y, count=6)
                    audio_mgr.play_sfx("skid", volume_scale=0.5)
                    camera.add_shake(3.0)
