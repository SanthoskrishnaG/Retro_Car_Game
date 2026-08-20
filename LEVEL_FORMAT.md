# 🏁 Retro Racer Python — Custom Level Format Specification (.rrlevel / JSON)

Retro Racer Python supports externally authored circuit levels using both standard `.json` and native `.rrlevel` files stored in `assets/tracks/`.

---

## 📄 File Structure Overview

Each `.rrlevel` or `.json` level file defines track parameters, environmental themes, difficulty curves, traffic AI behaviors, checkpoint milestones, and geometric road segments.

```json
{
  "name": "Level 1 — City Rush",
  "description": "High-speed sprint through the downtown metropolis with wide lanes and steady traffic.",
  "road_width": 180,
  "lanes": 4,
  "target_distance": 5000.0,
  "traffic_density": 0.7,
  "enemy_speed_multiplier": 0.9,
  "environment": "city",
  "weather": "clear",
  "difficulty": "Easy",
  "fuel_availability": 1.2,
  "powerup_frequency": 1.2,
  "checkpoints": [1200.0, 2500.0, 3800.0, 4800.0],
  "target_laps": 1,
  "segments": [
    {
      "length": 1200.0,
      "curve": 0.0,
      "road_width": 180,
      "lanes": 4,
      "biome": "city",
      "traffic_density": 1.0,
      "hazard_rate": 0.1,
      "scenery_left": "scenery_building_1",
      "scenery_right": "scenery_street_lamp"
    },
    {
      "length": 1000.0,
      "curve": 0.25,
      "road_width": 180,
      "lanes": 4,
      "biome": "city",
      "traffic_density": 1.0,
      "hazard_rate": 0.2,
      "scenery_left": "scenery_oak_tree",
      "scenery_right": "scenery_building_2"
    }
  ]
}
```

---

## ⚙️ Schema Specification

### Top-Level Properties

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string` | `"Custom Level"` | Display name shown in menus and HUD |
| `description` | `string` | `""` | Lore and mission briefing |
| `road_width` | `integer` | `180` | Asphalt road width in logical pixels |
| `lanes` | `integer` | `4` | Number of traffic lanes |
| `target_distance` | `float` | `5000.0` | Finish line distance in meters |
| `traffic_density` | `float` | `1.0` | Traffic spawn rate multiplier |
| `enemy_speed_multiplier` | `float` | `1.0` | Traffic vehicle cruise speed multiplier |
| `environment` | `string` | `"city"` | Theme: `city`, `countryside`, `desert`, `mountain`, `night`, `rain`, `synthwave` |
| `weather` | `string` | `"clear"` | Weather type: `clear`, `rain`, `fog` |
| `difficulty` | `string` | `"Medium"` | Difficulty: `Easy`, `Medium`, `Hard`, `Expert`, `Master` |
| `fuel_availability` | `float` | `1.0` | Fuel pickup spawn multiplier |
| `powerup_frequency` | `float` | `1.0` | Collectible power-up frequency multiplier |
| `checkpoints` | `array<float>` | `[1500, 3000, 4500]` | Distances (meters) where checkpoints award bonus fuel and +1000 score |
| `target_laps` | `integer` | `1` | Total laps to complete |
| `segments` | `array<Segment>` | `[]` | Sequential road curvature & scenery geometry |

---

### Segment Properties

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `length` | `float` | `1200.0` | Segment distance in pixels |
| `curve` | `float` | `0.0` | Curvature from `-1.0` (Hard Left) to `+1.0` (Hard Right) |
| `road_width` | `integer` | `180` | Local road width override |
| `lanes` | `integer` | `4` | Local lane count override |
| `biome` | `string` | `"city"` | Segment biome theme |
| `traffic_density` | `float` | `1.0` | Segment traffic multiplier |
| `hazard_rate` | `float` | `0.2` | Probability of spawning oil slicks and road cones |
| `scenery_left` | `string` | `"scenery_oak_tree"` | Left shoulder scenery sprite |
| `scenery_right` | `string` | `"scenery_street_lamp"` | Right shoulder scenery sprite |

---

## 🎨 Supported Scenery Sprite Names

- `scenery_oak_tree`
- `scenery_pine_tree`
- `scenery_palm_tree`
- `scenery_cactus`
- `scenery_rock`
- `scenery_building_1`
- `scenery_building_2`
- `scenery_street_lamp`
- `scenery_grandstand`
- `scenery_billboard_retro`
- `scenery_billboard_nitro`
