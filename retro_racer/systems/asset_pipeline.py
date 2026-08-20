"""Procedural Pixel-Art Asset Pipeline for Retro Racer Python.

Generates crisp, retro 16-bit / 32-bit pixel sprites using Pillow & Pygame.
All sprites are generated dynamically on startup (or loaded from cache),
ensuring zero broken asset links and full cross-platform reliability.
"""

import math
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from PIL import Image, ImageDraw

from retro_racer.config import SPRITES_DIR, COLOR_ASPHALT, COLOR_WHITE, COLOR_RED, COLOR_YELLOW, COLOR_CYAN, COLOR_GREEN


class AssetPipeline:
    """Procedural generator and cache manager for game pixel sprites."""

    def __init__(self, cache_dir: Path = SPRITES_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._pygame_surfaces: Dict[str, any] = {}

    def get_surface(self, name: str, pygame_module=None):
        """Get a pygame Surface for the given sprite name."""
        if name in self._pygame_surfaces:
            return self._pygame_surfaces[name]

        img_path = self.cache_dir / f"{name}.png"
        if not img_path.exists():
            self.generate_all_sprites()

        if pygame_module is not None:
            surf = pygame_module.image.load(str(img_path)).convert_alpha()
            self._pygame_surfaces[name] = surf
            return surf
        return None

    def generate_all_sprites(self):
        """Generate the full suite of pixel-art sprites and save them to disk."""
        # 1. Player Cars
        self._generate_car("player_red", primary=(235, 45, 45), secondary=(255, 210, 50), detail=(30, 30, 40))
        self._generate_car("player_cyan", primary=(0, 220, 240), secondary=(255, 255, 255), detail=(20, 40, 60))
        self._generate_car("player_yellow", primary=(255, 200, 20), secondary=(20, 20, 25), detail=(60, 45, 10))
        self._generate_car("player_purple", primary=(170, 50, 230), secondary=(0, 240, 255), detail=(40, 15, 60))
        self._generate_car("player_black", primary=(35, 38, 48), secondary=(230, 45, 45), detail=(15, 15, 20))
        self._generate_car("player_green", primary=(40, 190, 80), secondary=(255, 255, 255), detail=(15, 60, 25))

        # 2. Traffic Cars
        self._generate_car("traffic_sedan_blue", primary=(50, 120, 220), secondary=(200, 220, 255), style="sedan")
        self._generate_car("traffic_sedan_white", primary=(230, 235, 245), secondary=(100, 110, 130), style="sedan")
        self._generate_car("traffic_sport_pink", primary=(245, 50, 140), secondary=(255, 255, 255), style="sport")
        self._generate_car("traffic_sport_orange", primary=(255, 130, 20), secondary=(30, 30, 35), style="sport")
        self._generate_car("traffic_taxi", primary=(255, 210, 20), secondary=(20, 20, 20), style="taxi")
        self._generate_car("traffic_police", primary=(245, 245, 250), secondary=(25, 25, 30), style="police")
        self._generate_truck("traffic_truck_red", cab_color=(220, 40, 40), trailer_color=(220, 225, 235))
        self._generate_truck("traffic_truck_blue", cab_color=(40, 90, 210), trailer_color=(190, 200, 215))

        # 3. Roadside Scenery
        self._generate_palm_tree("scenery_palm_tree")
        self._generate_pine_tree("scenery_pine_tree")
        self._generate_oak_tree("scenery_oak_tree")
        self._generate_street_lamp("scenery_street_lamp")
        self._generate_billboard("scenery_billboard_retro", "RETRO", (255, 40, 140))
        self._generate_billboard("scenery_billboard_nitro", "NITRO", (0, 220, 255))
        self._generate_building("scenery_building_1", (60, 70, 95), (255, 220, 100))
        self._generate_building("scenery_building_2", (85, 60, 90), (0, 230, 240))
        self._generate_cactus("scenery_cactus")
        self._generate_rock("scenery_rock")
        self._generate_grandstand("scenery_grandstand")

        # 4. Pickups & Hazards
        self._generate_fuel_can("pickup_fuel")
        self._generate_nitro_can("pickup_nitro")
        self._generate_coin("pickup_coin")
        self._generate_shield_icon("pickup_shield")
        self._generate_magnet_icon("pickup_magnet")
        self._generate_slowmo_icon("pickup_slowmo")
        self._generate_multiplier_icon("pickup_2x")
        self._generate_wrench_icon("pickup_wrench")
        self._generate_oil_slick("hazard_oil")
        self._generate_traffic_cone("hazard_cone")

        # 5. Visual Effects & Particles
        self._generate_nitro_flame("fx_nitro_flame")
        self._generate_explosion_frames("fx_explosion")
        self._generate_spark("fx_spark")
        self._generate_smoke("fx_smoke")

    def _generate_car(self, name: str, primary: Tuple[int, int, int], secondary: Tuple[int, int, int],
                      detail: Tuple[int, int, int] = (25, 25, 30), style: str = "sport"):
        """Draw top-down pixel-art vehicle with shading, highlights, glass, and wheels."""
        w, h = 34, 62
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Wheels (4 black rubber tires with grey rims)
        tire_color = (25, 25, 28)
        rim_color = (160, 170, 185)
        # Front tires
        draw.rectangle([2, 10, 6, 22], fill=tire_color)
        draw.rectangle([w - 7, 10, w - 3, 22], fill=tire_color)
        draw.line([4, 13, 4, 19], fill=rim_color)
        draw.line([w - 5, 13, w - 5, 19], fill=rim_color)
        # Rear tires
        draw.rectangle([2, 42, 6, 54], fill=tire_color)
        draw.rectangle([w - 7, 42, w - 3, 54], fill=tire_color)
        draw.line([4, 45, 4, 51], fill=rim_color)
        draw.line([w - 5, 45, w - 5, 51], fill=rim_color)

        # Main Chassis Base (Aerodynamic curved body)
        dark_shade = (max(0, primary[0] - 50), max(0, primary[1] - 50), max(0, primary[2] - 50))
        light_shade = (min(255, primary[0] + 50), min(255, primary[1] + 50), min(255, primary[2] + 50))

        # Body outline/shadow
        draw.rounded_rectangle([5, 4, w - 6, h - 4], radius=6, fill=dark_shade)
        # Body main coat
        draw.rounded_rectangle([6, 5, w - 7, h - 5], radius=5, fill=primary)
        # Body central highlight
        draw.rectangle([13, 7, w - 14, h - 8], fill=light_shade)

        # Racing stripes / secondary design
        if style == "sport":
            draw.rectangle([14, 5, 19, h - 5], fill=secondary)
        elif style == "taxi":
            # Checkerboard strip across roof
            for x in range(8, w - 8, 4):
                col = (20, 20, 20) if (x // 4) % 2 == 0 else (240, 240, 240)
                draw.rectangle([x, 26, x + 3, 30], fill=col)
            # Roof Taxi Light
            draw.rounded_rectangle([12, 28, w - 13, 34], radius=2, fill=(255, 240, 80))
            draw.rectangle([14, 30, w - 15, 32], fill=(40, 40, 40))
        elif style == "police":
            # White middle door / roof panel
            draw.rectangle([6, 18, w - 7, 42], fill=(245, 245, 250))
            # Roof Siren (Red & Blue)
            draw.rectangle([10, 28, 16, 33], fill=(240, 30, 30))
            draw.rectangle([17, 28, w - 11, 33], fill=(30, 80, 255))
            draw.rectangle([15, 29, 18, 32], fill=(255, 255, 255))
        elif style == "sedan":
            # Subtle chrome trim
            draw.line([7, 6, w - 8, 6], fill=(210, 220, 230))
            draw.line([7, h - 6, w - 8, h - 6], fill=(210, 220, 230))

        # Glass Windows (Tinted cyan/dark blue with reflection glint)
        glass_base = (30, 45, 65)
        glass_glint = (180, 220, 255)
        # Front Windshield
        draw.polygon([(9, 22), (w - 10, 22), (w - 8, 15), (7, 15)], fill=glass_base)
        draw.line([(10, 16), (15, 21)], fill=glass_glint, width=2)
        # Rear Window
        draw.polygon([(9, 44), (w - 10, 44), (w - 8, 50), (7, 50)], fill=glass_base)
        draw.line([(11, 46), (16, 49)], fill=glass_glint)
        # Side Windows
        draw.rectangle([7, 24, 9, 42], fill=glass_base)
        draw.rectangle([w - 10, 24, w - 8, 42], fill=glass_base)

        # Roof Panel
        draw.rectangle([10, 23, w - 11, 43], fill=primary)
        draw.line([11, 23, w - 12, 23], fill=dark_shade)
        draw.line([11, 43, w - 12, 43], fill=dark_shade)

        # Headlights & Taillights
        # Front yellow/white xenon beams
        draw.rectangle([7, 5, 11, 8], fill=(255, 255, 210))
        draw.rectangle([w - 12, 5, w - 8, 8], fill=(255, 255, 210))
        # Rear neon crimson brake lights
        draw.rectangle([7, h - 6, 12, h - 4], fill=(240, 20, 20))
        draw.rectangle([w - 13, h - 6, w - 8, h - 4], fill=(240, 20, 20))

        # Exhaust Pipes
        draw.rectangle([10, h - 4, 13, h - 2], fill=(160, 160, 160))
        draw.rectangle([w - 14, h - 4, w - 11, h - 2], fill=(160, 160, 160))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_truck(self, name: str, cab_color: Tuple[int, int, int], trailer_color: Tuple[int, int, int]):
        """Generate long multi-axle semi-truck sprite."""
        w, h = 42, 104
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Tires (3 pairs on trailer, 2 pairs on cab)
        tire_color = (25, 25, 28)
        # Trailer tires
        for ty in [60, 76, 90]:
            draw.rectangle([2, ty, 6, ty + 9], fill=tire_color)
            draw.rectangle([w - 7, ty, w - 3, ty + 9], fill=tire_color)
        # Cab tires
        for ty in [10, 30]:
            draw.rectangle([2, ty, 6, ty + 9], fill=tire_color)
            draw.rectangle([w - 7, ty, w - 3, ty + 9], fill=tire_color)

        # Cab Section (Front)
        draw.rounded_rectangle([6, 5, w - 7, 36], radius=4, fill=cab_color)
        # Cab Windshield
        draw.polygon([(9, 14), (w - 10, 14), (w - 8, 8), (7, 8)], fill=(35, 55, 80))
        draw.line([(10, 9), (18, 13)], fill=(180, 220, 255), width=2)
        # Cab Headlights
        draw.rectangle([7, 5, 12, 7], fill=(255, 255, 200))
        draw.rectangle([w - 13, 5, w - 8, 7], fill=(255, 255, 200))

        # Trailer Hitch Gap
        draw.rectangle([14, 37, w - 15, 42], fill=(50, 50, 55))

        # Cargo Container / Trailer
        draw.rectangle([5, 43, w - 6, h - 5], fill=trailer_color)
        # Container corrugation ridges
        dark_ridge = (max(0, trailer_color[0] - 35), max(0, trailer_color[1] - 35), max(0, trailer_color[2] - 35))
        for y in range(48, h - 8, 6):
            draw.line([6, y, w - 7, y], fill=dark_ridge)
        # Trailer Rear Hazard stripes & lights
        for x in range(7, w - 7, 5):
            col = (230, 40, 40) if (x // 5) % 2 == 0 else (240, 240, 240)
            draw.rectangle([x, h - 6, x + 4, h - 4], fill=col)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_palm_tree(self, name: str):
        """Tropical curved palm tree sprite."""
        w, h = 48, 56
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Shadow
        draw.ellipse([14, 46, 38, 54], fill=(0, 0, 0, 60))
        # Trunk
        draw.arc([16, 20, 44, 52], 180, 270, fill=(120, 80, 40), width=5)
        # Fronds / Leaves
        leaf_color = (30, 165, 60)
        leaf_dark = (15, 110, 40)
        draw.polygon([(24, 22), (6, 12), (14, 26)], fill=leaf_color)
        draw.polygon([(24, 22), (42, 10), (36, 24)], fill=leaf_dark)
        draw.polygon([(24, 22), (8, 30), (18, 32)], fill=leaf_dark)
        draw.polygon([(24, 22), (40, 28), (32, 34)], fill=leaf_color)
        draw.polygon([(24, 22), (24, 4), (28, 14)], fill=leaf_color)
        # Coconuts
        draw.ellipse([22, 20, 25, 23], fill=(90, 55, 25))
        draw.ellipse([25, 21, 28, 24], fill=(90, 55, 25))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_pine_tree(self, name: str):
        """Tiered evergreen pine tree sprite."""
        w, h = 44, 58
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Shadow
        draw.ellipse([10, 48, 34, 56], fill=(0, 0, 0, 60))
        # Trunk
        draw.rectangle([20, 42, 24, 52], fill=(95, 60, 35))
        # 3 Green Foliage Triangles
        c1, c2 = (25, 120, 55), (15, 85, 38)
        # Bottom tier
        draw.polygon([(22, 26), (6, 44), (38, 44)], fill=c2)
        draw.polygon([(22, 26), (12, 44), (32, 44)], fill=c1)
        # Middle tier
        draw.polygon([(22, 14), (10, 32), (34, 32)], fill=c2)
        draw.polygon([(22, 14), (15, 32), (29, 32)], fill=c1)
        # Top tier
        draw.polygon([(22, 4), (14, 20), (30, 20)], fill=c2)
        draw.polygon([(22, 4), (18, 20), (26, 20)], fill=c1)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_oak_tree(self, name: str):
        """Lush round deciduous oak tree."""
        w, h = 52, 58
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Shadow
        draw.ellipse([12, 48, 40, 56], fill=(0, 0, 0, 60))
        # Trunk
        draw.rectangle([23, 38, 29, 52], fill=(105, 70, 40))
        # Canopy clusters
        c_dark = (25, 130, 50)
        c_mid = (45, 175, 70)
        c_light = (85, 215, 100)
        draw.ellipse([8, 14, 36, 40], fill=c_dark)
        draw.ellipse([20, 12, 44, 38], fill=c_dark)
        draw.ellipse([12, 6, 40, 32], fill=c_mid)
        draw.ellipse([16, 8, 34, 24], fill=c_light)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_street_lamp(self, name: str):
        """Retro metallic street lamp with glowing neon bulb."""
        w, h = 26, 64
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Shadow
        draw.ellipse([6, 58, 20, 62], fill=(0, 0, 0, 50))
        # Pole
        draw.rectangle([11, 8, 14, 60], fill=(110, 115, 125))
        # Arm
        draw.rectangle([11, 6, 23, 10], fill=(110, 115, 125))
        # Fixture & Bulb
        draw.rectangle([18, 10, 24, 15], fill=(40, 40, 45))
        draw.rectangle([19, 13, 23, 17], fill=(255, 245, 130))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_billboard(self, name: str, text: str, border_color: Tuple[int, int, int]):
        """Synthwave retro advertising billboard."""
        w, h = 64, 48
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Posts
        draw.rectangle([14, 32, 17, 46], fill=(80, 85, 95))
        draw.rectangle([46, 32, 49, 46], fill=(80, 85, 95))
        # Board
        draw.rectangle([4, 4, 59, 32], fill=(20, 20, 28))
        draw.rectangle([6, 6, 57, 30], outline=border_color, width=2)
        # Synth grid or text stripes inside billboard
        draw.line([10, 18, 54, 18], fill=border_color, width=2)
        draw.rectangle([20, 11, 44, 25], fill=border_color)
        draw.rectangle([22, 13, 42, 23], fill=(15, 15, 22))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_building(self, name: str, facade: Tuple[int, int, int], window_col: Tuple[int, int, int]):
        """Pixel skyscraper block with illuminated grid windows."""
        w, h = 68, 80
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Building Facade
        draw.rectangle([4, 4, w - 5, h - 1], fill=facade)
        # Roof rim
        draw.rectangle([2, 2, w - 3, 6], fill=(min(255, facade[0] + 30), min(255, facade[1] + 30), min(255, facade[2] + 30)))
        # Window Grid
        for r in range(12, h - 8, 10):
            for c in range(10, w - 12, 11):
                # 80% illuminated windows
                is_on = ((r * 7 + c * 13) % 5) != 0
                col = window_col if is_on else (max(0, facade[0] - 25), max(0, facade[1] - 25), max(0, facade[2] - 25))
                draw.rectangle([c, r, c + 6, r + 5], fill=col)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_cactus(self, name: str):
        """Desert Saguaro cactus sprite."""
        w, h = 36, 52
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        col = (45, 135, 65)
        dark = (28, 95, 45)
        # Shadow
        draw.ellipse([8, 44, 28, 50], fill=(0, 0, 0, 50))
        # Main Trunk
        draw.rounded_rectangle([15, 6, 21, 46], radius=3, fill=col)
        draw.line([16, 8, 16, 44], fill=dark)
        # Left Arm
        draw.rectangle([7, 18, 15, 23], fill=col)
        draw.rounded_rectangle([7, 12, 12, 23], radius=2, fill=col)
        # Right Arm
        draw.rectangle([21, 24, 29, 29], fill=col)
        draw.rounded_rectangle([24, 16, 29, 29], radius=2, fill=col)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_rock(self, name: str):
        """Desert/mountain rock boulder."""
        w, h = 32, 24
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.ellipse([4, 12, 28, 22], fill=(0, 0, 0, 50))
        draw.polygon([(6, 18), (12, 6), (24, 8), (28, 16), (20, 20)], fill=(120, 105, 95))
        draw.polygon([(12, 6), (20, 8), (17, 15), (9, 14)], fill=(155, 140, 130))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_grandstand(self, name: str):
        """Roadside grandstand with cheering crowd."""
        w, h = 64, 52
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Stand structure
        draw.rectangle([4, 14, 59, 48], fill=(90, 95, 110))
        # Canopy roof
        draw.polygon([(2, 14), (61, 14), (56, 4), (7, 4)], fill=(210, 50, 50))
        # Seating tiers with colored dots representing people
        crowd_colors = [(240, 80, 80), (80, 160, 240), (240, 220, 60), (240, 240, 240), (90, 210, 100)]
        for row in range(18, 44, 6):
            draw.line([6, row + 4, 57, row + 4], fill=(60, 65, 75))
            for x in range(8, 56, 4):
                col = crowd_colors[(row * 5 + x * 3) % len(crowd_colors)]
                draw.rectangle([x, row, x + 2, row + 3], fill=col)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_fuel_can(self, name: str):
        """Red Jerrycan Fuel Pickup Sprite."""
        w, h = 28, 30
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Glow shadow
        draw.ellipse([4, 22, 24, 28], fill=(0, 0, 0, 60))
        # Canister Body
        draw.rounded_rectangle([6, 8, 22, 26], radius=3, fill=(230, 45, 45))
        draw.rectangle([8, 10, 20, 24], outline=(170, 25, 25), width=1)
        # Handle & Spout
        draw.rectangle([9, 4, 19, 8], outline=(180, 30, 30), width=1)
        draw.rectangle([17, 2, 21, 6], fill=(220, 220, 230))
        # 'F' letter
        draw.line([11, 13, 11, 21], fill=(255, 255, 255), width=2)
        draw.line([11, 13, 17, 13], fill=(255, 255, 255), width=2)
        draw.line([11, 17, 15, 17], fill=(255, 255, 255), width=2)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_nitro_can(self, name: str):
        """Blue Nitrous Oxide Tank Sprite."""
        w, h = 28, 30
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Glow shadow
        draw.ellipse([4, 22, 24, 28], fill=(0, 0, 0, 60))
        # Blue Bottle Body
        draw.rounded_rectangle([7, 8, 21, 26], radius=4, fill=(0, 160, 240))
        draw.line([10, 10, 10, 24], fill=(160, 230, 255), width=2)
        # Silver Valve
        draw.rectangle([11, 3, 17, 8], fill=(200, 205, 215))
        draw.rectangle([13, 1, 15, 4], fill=(240, 240, 250))
        # Lightning / N2O bolt
        draw.polygon([(15, 11), (11, 18), (14, 18), (12, 24), (17, 16), (14, 16)], fill=(255, 255, 255))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_coin(self, name: str):
        """Gold coin collectible sprite."""
        w, h = 24, 24
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.ellipse([2, 2, 21, 21], fill=(255, 195, 0))
        draw.ellipse([4, 4, 19, 19], outline=(230, 150, 0), width=2)
        # Center Star / Dollar symbol
        draw.rectangle([10, 7, 13, 16], fill=(255, 235, 130))
        draw.rectangle([8, 9, 15, 14], fill=(255, 235, 130))
        # Glint
        draw.point([(6, 6), (7, 6), (6, 7)], fill=(255, 255, 255))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_shield_icon(self, name: str):
        """Hexagonal glowing shield bubble icon."""
        w, h = 28, 28
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        pts = [(14, 2), (25, 7), (25, 20), (14, 26), (3, 20), (3, 7)]
        draw.polygon(pts, fill=(0, 200, 255, 120), outline=(0, 240, 255))
        draw.polygon([(14, 6), (21, 10), (21, 18), (14, 22), (7, 18), (7, 10)], outline=(255, 255, 255))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_magnet_icon(self, name: str):
        """Horseshoe Magnet sprite."""
        w, h = 28, 28
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Red Arch
        draw.arc([4, 4, 23, 23], 0, 180, fill=(230, 40, 40), width=6)
        draw.rectangle([4, 13, 9, 21], fill=(230, 40, 40))
        draw.rectangle([18, 13, 23, 21], fill=(230, 40, 40))
        # Silver Poles
        draw.rectangle([4, 19, 9, 24], fill=(220, 225, 235))
        draw.rectangle([18, 19, 23, 24], fill=(220, 225, 235))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_slowmo_icon(self, name: str):
        """Hourglass / Clock Slow-Mo sprite."""
        w, h = 28, 28
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Cyan clock ring
        draw.ellipse([3, 3, 24, 24], fill=(20, 40, 60), outline=(0, 230, 255), width=2)
        # Clock Hands
        draw.line([14, 14, 14, 7], fill=(255, 255, 255), width=2)
        draw.line([14, 14, 19, 14], fill=(0, 230, 255), width=2)
        draw.point([14, 14], fill=(255, 255, 255))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_multiplier_icon(self, name: str):
        """Golden '2X' multiplier badge."""
        w, h = 28, 28
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.ellipse([2, 2, 25, 25], fill=(255, 170, 0), outline=(255, 220, 50), width=2)
        # '2'
        draw.line([6, 9, 11, 9], fill=(255, 255, 255), width=2)
        draw.line([11, 9, 6, 17], fill=(255, 255, 255), width=2)
        draw.line([6, 17, 12, 17], fill=(255, 255, 255), width=2)
        # 'X'
        draw.line([15, 9, 21, 17], fill=(255, 255, 255), width=2)
        draw.line([21, 9, 15, 17], fill=(255, 255, 255), width=2)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_wrench_icon(self, name: str):
        """Repair wrench sprite."""
        w, h = 28, 28
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.line([6, 21, 18, 9], fill=(180, 190, 205), width=4)
        # Head
        draw.ellipse([14, 4, 24, 14], fill=(190, 200, 215))
        draw.ellipse([17, 7, 21, 11], fill=(0, 0, 0, 0))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_oil_slick(self, name: str):
        """Iridescent dark oil puddle hazard."""
        w, h = 42, 28
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.ellipse([3, 4, 38, 23], fill=(20, 22, 26, 220))
        draw.ellipse([8, 8, 30, 18], fill=(45, 30, 55, 180))
        draw.arc([10, 7, 28, 16], 30, 150, fill=(0, 220, 200, 200), width=2)
        draw.arc([14, 11, 33, 20], 210, 330, fill=(220, 40, 180, 180), width=2)

        img.save(self.cache_dir / f"{name}.png")

    def _generate_traffic_cone(self, name: str):
        """Orange roadside construction cone."""
        w, h = 24, 24
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Black Base
        draw.rectangle([4, 18, 19, 22], fill=(30, 30, 35))
        # Orange Cone
        draw.polygon([(12, 3), (6, 19), (18, 19)], fill=(255, 120, 10))
        # White reflective band
        draw.polygon([(10, 10), (14, 10), (16, 15), (8, 15)], fill=(245, 245, 250))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_nitro_flame(self, name: str):
        """Nitro blue-cyan thruster jet flame."""
        w, h = 20, 32
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Outer blue plume
        draw.polygon([(10, 30), (2, 4), (18, 4)], fill=(0, 120, 255, 200))
        # Inner cyan core
        draw.polygon([(10, 22), (5, 4), (15, 4)], fill=(0, 240, 255, 240))
        # Center white hot spot
        draw.polygon([(10, 14), (7, 4), (13, 4)], fill=(255, 255, 255))

        img.save(self.cache_dir / f"{name}.png")

    def _generate_explosion_frames(self, name: str):
        """8-frame explosion animation sprite strip."""
        fw, fh = 48, 48
        num_frames = 8
        strip = Image.new("RGBA", (fw * num_frames, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(strip)

        for i in range(num_frames):
            ox = i * fw
            cx, cy = ox + fw // 2, fh // 2
            progress = (i + 1) / num_frames
            max_r = int(22 * math.sin(progress * math.pi))

            if max_r > 2:
                # Outer fire orange
                draw.ellipse([cx - max_r, cy - max_r, cx + max_r, cy + max_r], fill=(255, 80 + int(i * 15), 0, 220))
                # Mid yellow
                r_mid = max(1, int(max_r * 0.7))
                draw.ellipse([cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid], fill=(255, 220, 40, 240))
                # Inner white flash
                if i < 4:
                    r_core = max(1, int(max_r * 0.4))
                    draw.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=(255, 255, 255, 255))

                # Scattered debris sparks
                for k in range(6):
                    ang = k * (math.pi / 3) + i * 0.5
                    dist = max_r + int(i * 3)
                    sx = cx + int(math.cos(ang) * dist)
                    sy = cy + int(math.sin(ang) * dist)
                    draw.point([(sx, sy), (sx + 1, sy)], fill=(255, 210, 60))

        strip.save(self.cache_dir / f"{name}.png")

    def _generate_spark(self, name: str):
        """Single collision spark."""
        w, h = 12, 12
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.line([6, 1, 6, 10], fill=(255, 240, 100), width=2)
        draw.line([1, 6, 10, 6], fill=(255, 240, 100), width=2)
        draw.point([6, 6], fill=(255, 255, 255))
        img.save(self.cache_dir / f"{name}.png")

    def _generate_smoke(self, name: str):
        """Soft smoke particle."""
        w, h = 16, 16
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([2, 2, 13, 13], fill=(180, 185, 195, 140))
        draw.ellipse([4, 4, 11, 11], fill=(220, 225, 230, 180))
        img.save(self.cache_dir / f"{name}.png")
