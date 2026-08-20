"""Active Racing Gameplay State."""

from typing import Optional
import pygame

from retro_racer.engine.state_manager import State
from retro_racer.entities.player import PlayerCar
from retro_racer.world.road import RoadManager
from retro_racer.world.spawner import WorldSpawner
from retro_racer.world.collision import CollisionSystem
from retro_racer.world.environment import get_environment_theme
from retro_racer.entities.particles import ParticleSystem
from retro_racer.engine.camera import Camera
from retro_racer.ui.hud import HUD
from retro_racer.ui.menu import MenuButton
from retro_racer.systems.level_editor import TrackData
from retro_racer.config import (
    ROAD_CENTER_X, VIRTUAL_WIDTH, VIRTUAL_HEIGHT,
    COLOR_WHITE, COLOR_CYAN, COLOR_YELLOW, COLOR_RED, COLOR_GOLD
)


class PlayState(State):
    """Core racing loop handling physics, AI, HUD, particle effects, and collisions."""

    def __init__(self, engine):
        super().__init__(engine)
        self.camera = Camera()
        self.hud = HUD()
        self.particle_system = ParticleSystem()
        self.road_system = RoadManager()
        self.spawner = WorldSpawner(self.road_system)

        self.player: Optional[PlayerCar] = None
        self.track_data: Optional[TrackData] = None
        self.theme = get_environment_theme("city")

        # Pause Menu
        self.is_paused = False
        self.pause_buttons = []
        self.pause_selected_idx = 0
        self._init_pause_menu()

    def _init_pause_menu(self):
        btn_w, btn_h = 130, 22
        cx = (VIRTUAL_WIDTH - btn_w) // 2
        self.pause_buttons = [
            MenuButton(pygame.Rect(cx, 85, btn_w, btn_h), "RESUME", "resume", font_size=11),
            MenuButton(pygame.Rect(cx, 112, btn_w, btn_h), "RESTART", "restart", font_size=11),
            MenuButton(pygame.Rect(cx, 139, btn_w, btn_h), "MAIN MENU", "menu", font_size=11, primary_color=COLOR_RED),
        ]

    def on_enter(self, track_data: Optional[TrackData] = None, seed: Optional[int] = None, **kwargs):
        self.is_paused = False
        self.particle_system.clear()

        # Load Track
        if track_data:
            self.track_data = track_data
            self.road_system.load_track(track_data)
        else:
            tracks = self.engine.level_editor.list_tracks()
            self.track_data = tracks[0] if tracks else None
            if self.track_data:
                self.road_system.load_track(self.track_data)

        self.theme = get_environment_theme(self.road_system.biome)

        # Career vehicle & upgrades
        profile = self.engine.db.get_career_profile()
        car_sprite = profile.get("selected_car", "player_red")

        self.player = PlayerCar(ROAD_CENTER_X, 0.0, sprite_name=car_sprite)
        self.player.apply_upgrades(profile)

        # Spawner with deterministic seed if provided
        self.spawner.reset(start_y=0.0, seed=seed)

        # Start Replay Recording
        self.engine.replay_mgr.start_recording(
            track_name=self.road_system.track_name,
            car_model=car_sprite,
            player_name=profile.get("player_name", "Racer 1")
        )

        # Audio
        self.engine.audio_mgr.start_music()

    def on_exit(self):
        self.engine.audio_mgr.stop_engine()

    def handle_events(self, events: list):
        input_mgr = self.engine.input_handler
        debug = self.engine.debug

        # Restart hotkey
        if input_mgr.is_action_just_pressed("restart"):
            self.engine.audio_mgr.play_sfx("beep")
            self.on_enter(self.track_data)
            return

        # Pause Toggle
        if input_mgr.is_action_just_pressed("pause"):
            self.is_paused = not self.is_paused
            self.engine.audio_mgr.play_sfx("beep")
            return

        # F3 Debug (Hitboxes)
        if input_mgr.is_action_just_pressed("debug") or input_mgr.is_just_pressed(pygame.K_F3):
            debug.toggle()

        # F4 Debug (Object boundaries)
        if input_mgr.is_action_just_pressed("debug_boundaries") or input_mgr.is_just_pressed(pygame.K_F4):
            debug.toggle_boundaries()

        # Debug Cheats
        if debug.enabled:
            if input_mgr.is_just_pressed(pygame.K_g):
                debug.toggle_god_mode()
                self.engine.audio_mgr.play_sfx("beep")
            elif input_mgr.is_just_pressed(pygame.K_n):
                debug.toggle_infinite_nitro()
                self.engine.audio_mgr.play_sfx("beep")
            elif input_mgr.is_just_pressed(pygame.K_h):
                debug.toggle_hitboxes()
                self.engine.audio_mgr.play_sfx("beep")
            elif input_mgr.is_just_pressed(pygame.K_t):
                self.spawner._spawn_traffic_car(self.player.position_y, difficulty=1.5)
            elif input_mgr.is_just_pressed(pygame.K_u):
                self.spawner._spawn_pickup(self.player.position_y)

        # Pause Menu Navigation
        if self.is_paused:
            if input_mgr.is_action_just_pressed("accelerate"):
                self.pause_selected_idx = (self.pause_selected_idx - 1) % len(self.pause_buttons)
                self.engine.audio_mgr.play_sfx("beep")
            elif input_mgr.is_action_just_pressed("brake"):
                self.pause_selected_idx = (self.pause_selected_idx + 1) % len(self.pause_buttons)
                self.engine.audio_mgr.play_sfx("beep")
            elif input_mgr.is_action_just_pressed("confirm"):
                self._handle_pause_action(self.pause_buttons[self.pause_selected_idx].action_id)

            for i, btn in enumerate(self.pause_buttons):
                if btn.check_hover(input_mgr.mouse_pos):
                    self.pause_selected_idx = i
                    if input_mgr.mouse_just_pressed:
                        self._handle_pause_action(btn.action_id)

    def _handle_pause_action(self, action_id: str):
        self.engine.audio_mgr.play_sfx("beep")
        if action_id == "resume":
            self.is_paused = False
        elif action_id == "restart":
            self.on_enter(self.track_data)
        elif action_id == "menu":
            self.engine.state_mgr.change_state("title")

    def update(self, dt: float):
        if self.is_paused:
            return

        input_mgr = self.engine.input_handler
        debug = self.engine.debug

        # Slow-mo effect
        time_scale = 0.5 if self.player.slowmo_timer > 0 else 1.0
        scaled_dt = dt * time_scale

        if debug.infinite_nitro:
            self.player.nitro = 100.0

        # 1. Road Geometry Bounds at Player
        _, road_left, road_right = self.road_system.get_road_bounds(self.player.position_y)
        curve = self.road_system.get_curvature_at(self.player.position_y)

        # 2. Player Physics Update
        self.player.update_physics(
            dt=scaled_dt,
            steer_input=input_mgr.steer,
            throttle=input_mgr.throttle,
            brake=input_mgr.brake,
            nitro_req=input_mgr.nitro,
            road_left=road_left,
            road_right=road_right,
            particle_system=self.particle_system,
            audio_mgr=self.engine.audio_mgr
        )

        speed_ratio = self.player.speed / max(1.0, self.player.max_speed)
        self.engine.audio_mgr.set_engine_rpm(speed_ratio)

        # 3. Spawner Update
        self.spawner.update(scaled_dt, self.player.position_y, self.player.distance)

        # 4. Traffic AI Update
        for traffic in self.spawner.traffic_cars:
            traffic.update_ai(scaled_dt, self.spawner.traffic_cars, player=self.player, road_left=road_left, road_right=road_right)

        # 5. Pickups & Hazards Update
        for p in self.spawner.pickups:
            p.update(scaled_dt, self.player.position_x, self.player.position_y, magnet_active=(self.player.magnet_timer > 0))

        # 6. Particle System Update
        self.particle_system.update(scaled_dt)

        # 7. Collision Detection (Player vs Enemy, Player vs Roadside, Enemy vs Enemy, Pickups, Hazards)
        if not debug.god_mode:
            CollisionSystem.process_player_traffic(
                self.player, self.spawner.traffic_cars,
                self.engine.audio_mgr, self.particle_system, self.camera, self.engine.renderer
            )
            CollisionSystem.process_player_roadside(
                self.player, self.spawner.roadside_objects,
                self.engine.audio_mgr, self.particle_system, self.camera, self.engine.renderer
            )
            CollisionSystem.process_hazards(
                self.player, self.spawner.hazards,
                self.engine.audio_mgr, self.particle_system, self.camera, self.engine.renderer
            )

        CollisionSystem.process_enemy_enemy(self.spawner.traffic_cars, self.particle_system, self.engine.audio_mgr)
        CollisionSystem.process_pickups(self.player, self.spawner.pickups, self.engine.audio_mgr, self.engine.renderer)

        # 8. Dynamic Camera
        self.camera.update(scaled_dt, self.player.position_x, self.player.position_y, curve)

        # 9. Renderer Speed Lines & Popups
        self.engine.renderer.update(scaled_dt, is_high_speed=self.player.is_nitro_active, speed_ratio=speed_ratio)

        # 10. Record Replay Frame
        self.engine.replay_mgr.record_frame({
            "player_x": self.player.position_x,
            "player_y": self.player.position_y,
            "speed": self.player.speed,
            "fuel": self.player.fuel,
            "nitro": self.player.nitro,
            "score": self.player.score,
            "health": self.player.health,
            "nitro_active": self.player.is_nitro_active,
            "traffic": [{"x": t.position_x, "y": t.position_y, "spr": t.sprite_name} for t in self.spawner.traffic_cars]
        })

        # 11. Check Game Over Condition
        if (self.player.fuel <= 0 or self.player.health <= 0 or self.player.is_crashed) and not debug.god_mode:
            rpl_path = self.engine.replay_mgr.stop_recording(self.player.score, self.player.distance)
            self.engine.state_mgr.change_state("game_over",
                                              score=self.player.score,
                                              distance=self.player.distance,
                                              track_name=self.road_system.track_name,
                                              car_model=self.player.sprite_name,
                                              replay_path=rpl_path)

    def render(self, surface: pygame.Surface):
        # 1. Road & Ground
        self.road_system.render(surface, self.camera, self.theme)

        # 2. Tire Skidmarks
        self.particle_system.render_skids(surface, self.camera)

        # 3. Roadside Scenery (Trees, Buildings, Billboards)
        for obj in self.spawner.roadside_objects:
            obj.render(surface, self.camera, self.engine.asset_pipeline)

        # 4. Hazards (Oil, Cones)
        for h in self.spawner.hazards:
            h.render(surface, self.camera, self.engine.asset_pipeline)

        # 5. Pickups (Fuel, Nitro, Coins)
        for p in self.spawner.pickups:
            p.render(surface, self.camera, self.engine.asset_pipeline)

        # 6. AI Traffic Vehicles
        for traffic in self.spawner.traffic_cars:
            traffic.render(surface, self.camera, self.engine.asset_pipeline)

        # 7. Player Car & Active Power-up Auras
        if self.player:
            self.player.render(surface, self.camera, self.engine.asset_pipeline, is_braking=self.player.is_braking)
            self.player.render_powerup_auras(surface, self.camera)

        # 8. Particle VFX (Sparks, Smoke, Fireball Explosions)
        self.particle_system.render_particles(surface, self.camera, self.engine.asset_pipeline)

        # 9. Speed Lines & Popups
        if self.player and (self.player.is_nitro_active or self.player.speed > 320.0):
            self.engine.renderer.render_speed_lines(surface, is_nitro=self.player.is_nitro_active)
        self.engine.renderer.render_floating_texts(surface)

        # 10. In-game HUD
        if self.player:
            self.hud.render(surface, self.player, self.road_system.track_name, self.road_system.total_length, self.engine.asset_pipeline)

        # 11. Debug Visualizer (F3 Hitboxes & F4 Object Boundaries)
        if self.engine.debug.enabled or self.engine.debug.show_boundaries:
            if self.player:
                stats = {
                    "fps": self.engine.clock.get_fps(),
                    "dt": self.engine.dt,
                    "pos_x": self.player.position_x,
                    "pos_y": self.player.position_y,
                    "vel_x": self.player.velocity_x,
                    "vel_y": self.player.velocity_y,
                    "speed": self.player.speed,
                    "speed_kmh": (self.player.speed / 380.0) * 220.0,
                    "fuel": self.player.fuel,
                    "nitro": self.player.nitro,
                    "health": self.player.health,
                    "score": self.player.score,
                    "track_name": self.road_system.track_name,
                    "curvature": self.road_system.get_curvature_at(self.player.position_y),
                    "traffic_count": len(self.spawner.traffic_cars),
                    "scenery_count": len(self.spawner.roadside_objects),
                }
                self.engine.debug.render(surface, stats)

            # F3 Collision Hitboxes
            if self.engine.debug.show_hitboxes:
                # Player
                psx, psy = self.camera.world_to_screen(self.player.position_x, self.player.position_y)
                phb = pygame.Rect(psx - self.player.width // 2, psy - self.player.height // 2, self.player.width, self.player.height)
                self.engine.debug.draw_hitbox(surface, phb, (0, 255, 0))

                # Traffic
                for t in self.spawner.traffic_cars:
                    tsx, tsy = self.camera.world_to_screen(t.position_x, t.position_y)
                    thb = pygame.Rect(tsx - t.width // 2, tsy - t.height // 2, t.width, t.height)
                    self.engine.debug.draw_hitbox(surface, thb, (255, 40, 40))

                # Pickups & Hazards
                for p in self.spawner.pickups:
                    px, py = self.camera.world_to_screen(p.x, p.y)
                    self.engine.debug.draw_hitbox(surface, pygame.Rect(px - p.width // 2, py - p.height // 2, p.width, p.height), (255, 220, 0))

                for h in self.spawner.hazards:
                    hx, hy = self.camera.world_to_screen(h.x, h.y)
                    self.engine.debug.draw_hitbox(surface, pygame.Rect(hx - h.width // 2, hy - h.height // 2, h.width, h.height), (255, 120, 0))

                # Roadside props
                for obj in self.spawner.roadside_objects:
                    ox, oy = self.camera.world_to_screen(obj.x, obj.y)
                    self.engine.debug.draw_hitbox(surface, pygame.Rect(ox - 8, oy - 9, 16, 18), (255, 100, 200))

            # F4 Object Boundaries & Lane Guides
            if self.engine.debug.show_boundaries:
                for t in self.spawner.traffic_cars:
                    tsx, tsy = self.camera.world_to_screen(t.position_x, t.position_y)
                    self.engine.debug.draw_boundary(surface, pygame.Rect(tsx - t.width // 2 - 2, tsy - t.height // 2 - 2, t.width + 4, t.height + 4), (0, 240, 255))

        # 12. Pause Menu Modal
        if self.is_paused:
            modal = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            modal.fill((10, 12, 20, 180))
            surface.blit(modal, (0, 0))

            p_title = self.hud.font_large.render("GAME PAUSED", True, COLOR_GOLD)
            surface.blit(p_title, (VIRTUAL_WIDTH // 2 - p_title.get_width() // 2, 55))

            for i, btn in enumerate(self.pause_buttons):
                btn.is_selected = (i == self.pause_selected_idx)
                btn.render(surface)
