# -*- coding: utf-8 -*-
"""
Ming Dynasty RPG - "开局一个碗，帮朱元璋打天下" (Starting with a Bowl)
Main Game Engine built with Pygame.
"""

from __future__ import annotations

import array
import math
import os
import sys
import json
from pathlib import Path
import pygame

# Import map data
from map_data import MAPS, MAP_WIDTH, MAP_HEIGHT
from enemy_renderer import draw_enemies

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ORIGINAL_TILE_SIZE = 32
SCALE_FACTOR = 2
TILE_SIZE = ORIGINAL_TILE_SIZE * SCALE_FACTOR  # 64x64 pixels

FPS = 60

# Game States
STATE_NORMAL = 0
STATE_DIALOGUE = 1
STATE_MENU = 2
STATE_EQUIP_CHOICE = 3
STATE_BATTLE = 4
STATE_STORY = 5

# Directions
DIR_DOWN = "down"
DIR_UP = "up"
DIR_LEFT = "left"
DIR_RIGHT = "right"

# Colors (NES Palette inspired)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (229, 57, 53)
COLOR_GOLD = (255, 193, 7)
COLOR_UI_BG = (16, 16, 24, 230)  # Dark translucent blue-grey
COLOR_UI_BORDER = (236, 239, 241) # Retro light grey
COLOR_TEXT = (255, 255, 255)

# Paths
BASE_DIR = Path(__file__).resolve().parent
TILES_DIR = BASE_DIR / "assets" / "tiles"
PLAYER_DIR = BASE_DIR / "assets" / "player"

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("大明王朝：开局一个碗 (Ming Dynasty RPG)")
clock = pygame.time.Clock()

# --- Retro Sound Generator ---
def play_beep(frequency: float, duration_ms: int, volume: float = 0.1) -> None:
    """Generates a retro square/sine wave in memory and plays it immediately."""
    try:
        sample_rate = 22050
        n_samples = int(sample_rate * (duration_ms / 1000.0))
        buf = array.array('h', [0] * n_samples)
        for i in range(n_samples):
            t = i / sample_rate
            # Sine wave with a bit of harmonics for retro feel
            val = int(32767 * volume * (0.7 * math.sin(2 * math.pi * frequency * t) + 
                                        0.3 * math.sin(4 * math.pi * frequency * t)))
            buf[i] = val
        sound = pygame.mixer.Sound(buffer=buf)
        sound.play()
    except Exception as e:
        # Fallback silently if audio device is busy or unavailable
        pass

def play_chime_success() -> None:
    """Plays a happy retro chime (perfect for opening treasure chest)."""
    play_beep(523.25, 100, 0.15) # C5
    pygame.time.wait(80)
    play_beep(659.25, 100, 0.15) # E5
    pygame.time.wait(80)
    play_beep(783.99, 100, 0.15) # G5
    pygame.time.wait(80)
    play_beep(1046.50, 200, 0.15) # C6

def play_chime_talk() -> None:
    """Plays a retro blip sound when talking to NPCs."""
    play_beep(600, 60, 0.1)
    pygame.time.wait(50)
    play_beep(800, 80, 0.1)

# --- Asset Manager ---
class AssetManager:
    def __init__(self) -> None:
        self.tiles: dict[str, pygame.Surface] = {}
        self.player_sprites: dict[str, list[pygame.Surface]] = {}
        self.npc_sprites: dict[str, pygame.Surface] = {}
        self.enemy_sprites: dict[str, dict[str, list[pygame.Surface]]] = {}
        self.load_assets()

    def load_image(self, path: Path, rotate_deg: int = 0) -> pygame.Surface:
        """Loads and scales an image. Falls back to a colored rect if file missing."""
        if path.exists():
            try:
                img = pygame.image.load(str(path)).convert_alpha()
                if rotate_deg != 0:
                    img = pygame.transform.rotate(img, rotate_deg)
                return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            except Exception as e:
                print(f"Error loading image {path}: {e}")
        
        # Fallback surface
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((120, 120, 120))
        pygame.draw.rect(surf, (200, 50, 50), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        return surf

    def load_assets(self) -> None:
        # Ground tile mappings
        ground_paths = {
            'g': TILES_DIR / "01_草地" / "普通草地.png",
            'f': TILES_DIR / "01_草地" / "带小花的草地.png",
            's': TILES_DIR / "01_草地" / "带石块的草地.png",
            'h': TILES_DIR / "01_草地" / "干草.png",
            'r': TILES_DIR / "02_石子路" / "直石子路.png",
            'v': (TILES_DIR / "02_石子路" / "直石子路.png", 90), # Rotate 90 for vertical road
            'c': TILES_DIR / "02_石子路" / "弯石子路.png",
            'x': TILES_DIR / "02_石子路" / "石子路交叉口.png",
            'w': TILES_DIR / "08_水域" / "平静的河面.png",
            'o': TILES_DIR / "08_水域" / "有波纹的流动河水.png",
            'a': TILES_DIR / "08_水域" / "有鹅卵石的浅水.png",
            'd': TILES_DIR / "08_水域" / "深水.png",
            'b': TILES_DIR / "08_水域" / "有波纹的流动河水.png", # Bridge base is flowing water!
        }

        for char, info in ground_paths.items():
            if isinstance(info, tuple):
                path, rot = info
                self.tiles[char] = self.load_image(path, rotate_deg=rot)
            else:
                self.tiles[char] = self.load_image(info)

        # Obstacle tile mappings
        obstacle_paths = {
            'T': TILES_DIR / "24_树木变体" / "橡树.png",
            'P': TILES_DIR / "24_树木变体" / "松树.png",
            'M': TILES_DIR / "24_树木变体" / "枫树.png",
            'K': TILES_DIR / "24_树木变体" / "枯树.png",
            'F': TILES_DIR / "07_村庄建筑" / "村庄围栏.png",
            'J': TILES_DIR / "07_村庄建筑" / "村庄水井.png",
            'S': TILES_DIR / "10_互动道具" / "木制路标.png",
            'B': TILES_DIR / "10_互动道具" / "篝火.png",
            'U': TILES_DIR / "10_互动道具" / "木桶.png",
            'X': TILES_DIR / "10_互动道具" / "破损的木车.png",
            'R': TILES_DIR / "07_村庄建筑" / "茅草屋顶.png",
            'W': TILES_DIR / "07_村庄建筑" / "木墙.png",
            'D': TILES_DIR / "07_村庄建筑" / "木门.png",
            'Y': TILES_DIR / "10_互动道具" / "小石碑.png",
            'C': TILES_DIR / "18_废墟" / "废墟中的宝箱.png",
            'm': TILES_DIR / "11_农田" / "整齐的麦田.png",
            'i': TILES_DIR / "11_农田" / "稻田.png",
            'v': TILES_DIR / "11_农田" / "菜地.png",
        }

        for char, path in obstacle_paths.items():
            self.tiles[char] = self.load_image(path)

        # Load Player Sprites (down, up, left, right; frames 0, 1, 2)
        for direction in [DIR_DOWN, DIR_UP, DIR_LEFT, DIR_RIGHT]:
            self.player_sprites[direction] = []
            for frame in range(3):
                sprite_path = PLAYER_DIR / f"{direction}_{frame}.png"
                self.player_sprites[direction].append(self.load_image(sprite_path))

        # Load NPC Sprites
        npcs_dir = BASE_DIR / "assets" / "npcs"
        # Auto-generate if missing
        if not (npcs_dir / "wolf.png").exists():
            try:
                from tools.generate_npcs import main as gen_npcs
                gen_npcs()
            except Exception as e:
                print(f"Error auto-generating npcs: {e}")

        for npc_id in ["friend", "elder", "monk", "chang", "merchant", "farmer", "wolf", "tiger", "lion"]:
            npc_path = npcs_dir / f"{npc_id}.png"
            self.npc_sprites[npc_id] = self.load_image(npc_path)

        # Load Enemy Sprites
        enemies_dir = BASE_DIR / "assets" / "enemies"
        # Auto-generate if missing
        if not (enemies_dir / "yuan_soldier" / "down_0.png").exists():
            try:
                from tools.generate_enemies import main as gen_enemies
                gen_enemies()
            except Exception as e:
                print(f"Error auto-generating enemies: {e}")

        for enemy_id in ["yuan_soldier", "yuan_boss", "yuan_emperor"]:
            self.enemy_sprites[enemy_id] = {}
            for direction in [DIR_DOWN, DIR_UP, DIR_LEFT, DIR_RIGHT]:
                self.enemy_sprites[enemy_id][direction] = []
                for frame in range(3):
                    sprite_path = enemies_dir / enemy_id / f"{direction}_{frame}.png"
                    self.enemy_sprites[enemy_id][direction].append(self.load_image(sprite_path))

# --- Player Class ---
class Player:
    def __init__(self, grid_x: int, grid_y: int) -> None:
        self.grid_x = grid_x
        self.grid_y = grid_y
        
        # Pixel coordinates for smooth sliding movement
        self.pixel_x = grid_x * TILE_SIZE
        self.pixel_y = grid_y * TILE_SIZE
        
        self.target_grid_x = grid_x
        self.target_grid_y = grid_y
        
        self.direction = DIR_DOWN
        self.is_moving = False
        self.move_speed = 4  # Pixels per frame (must divide TILE_SIZE=64 evenly)
        
        # Animation
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 10  # Frames per animation step

        # RPG Stats
        self.name = "朱元璋"
        self.level = 1
        self.exp = 0
        self.gold = 0
        self.inventory: list[str] = ["乞讨用的破碗"]
        self.idle_timer = 0
        self.is_afk_enabled = True  # Toggle for AFK
        self.max_hp = 150
        self.hp = 150
        
        # Equipment Slots
        self.equipment: dict[str, str | None] = {
            "武器": "乞讨用的破碗",
            "护腕": None,
            "项链": None,
            "护符": None,
            "戒指": None,
            "帽子": None,
            "护手": None,
            "护肩": None,
            "腰带": None,
            "靴子": None
        }

    @property
    def weapon(self) -> str:
        return self.equipment.get("武器") or "乞讨用的破碗"

    @weapon.setter
    def weapon(self, val: str) -> None:
        self.equipment["武器"] = val

    @property
    def attack(self) -> int:
        base = self.level * 5
        # Calculate offensive items stats dynamically
        bonus = 0
        for slot, item_name in self.equipment.items():
            if item_name and slot in ["武器", "护腕", "项链", "护符", "戒指"]:
                # Fetch attack from equipment table if loaded, otherwise hardcoded default fallback
                bonus += getattr(self, "loaded_atk_stats", {}).get(item_name, 0)
        
        # Default fallback if stats not loaded yet
        if bonus == 0:
            if self.weapon == "破旧的木棍":
                bonus = 12
            elif self.weapon == "精致的铁剑":
                bonus = 25
            else:
                bonus = 2
        return base + bonus

    @property
    def defense(self) -> int:
        base = self.level * 3
        # Calculate defensive items stats dynamically
        bonus = 0
        for slot, item_name in self.equipment.items():
            if item_name and slot in ["帽子", "护手", "护肩", "腰带", "靴子"]:
                bonus += getattr(self, "loaded_def_stats", {}).get(item_name, 0)
                
        # Default fallback
        if bonus == 0:
            if self.equipment.get("靴子") == "精致的草鞋" or "精致的草鞋" in self.inventory:
                bonus = 10
        return base + bonus

    def gain_exp(self, amount: int) -> bool:
        """Gains experience points and checks for level up."""
        self.exp += amount
        needed = self.level * 100
        leveled_up = False
        while self.exp >= needed:
            self.exp -= needed
            self.level += 1
            self.max_hp = self.level * 50 + 100
            self.hp = self.max_hp
            needed = self.level * 100
            leveled_up = True
        return leveled_up

    def update(self) -> bool:
        """Updates player positions and generates idle/AFK experience. Returns True on level up."""
        leveled_up_from_afk = False
        if self.is_afk_enabled:
            self.idle_timer += 1
            if self.idle_timer >= 60:  # Every 60 frames (1 second at 60 FPS)
                self.idle_timer = 0
                leveled_up_from_afk = self.gain_exp(5)  # Let's give 5 EXP per second of idle/AFK!
            
        if self.is_moving:
            # Move pixel coordinates towards target grid coordinates
            target_pixel_x = self.target_grid_x * TILE_SIZE
            target_pixel_y = self.target_grid_y * TILE_SIZE
            
            if self.pixel_x < target_pixel_x:
                self.pixel_x += self.move_speed
            elif self.pixel_x > target_pixel_x:
                self.pixel_x -= self.move_speed
                
            if self.pixel_y < target_pixel_y:
                self.pixel_y += self.move_speed
            elif self.pixel_y > target_pixel_y:
                self.pixel_y -= self.move_speed
                
            # Check if reached target
            if self.pixel_x == target_pixel_x and self.pixel_y == target_pixel_y:
                self.grid_x = self.target_grid_x
                self.grid_y = self.target_grid_y
                self.is_moving = False
                self.anim_frame = 0  # Reset to standing frame
                
            # Cycle walking animation frames (1 -> 0 -> 2 -> 0 -> 1...)
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            self.anim_frame = 0

        return leveled_up_from_afk

    def get_current_sprite_frame(self) -> int:
        if self.anim_frame == 0 or self.anim_frame == 2:
            return 0
        elif self.anim_frame == 1:
            return 1
        else:
            return 2

    def move(self, dx: int, dy: int, direction: str, collision_checker: callable, transition_trigger: callable = None) -> None:
        if self.is_moving:
            return
            
        self.direction = direction
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy
        
        # Check boundaries and obstacles
        if 0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT:
            if not collision_checker(target_x, target_y):
                self.target_grid_x = target_x
                self.target_grid_y = target_y
                self.is_moving = True
                self.anim_frame = 1
                self.anim_timer = 0
        elif transition_trigger:
            # Out of bounds - trigger map transition check
            transition_trigger(target_x, target_y)

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int, sprites: dict[str, list[pygame.Surface]]) -> None:
        frame_idx = self.get_current_sprite_frame()
        sprite = sprites[self.direction][frame_idx]
        screen_pos_x = self.pixel_x - camera_x
        screen_pos_y = self.pixel_y - camera_y
        surface.blit(sprite, (screen_pos_x, screen_pos_y))

# --- Enemy Class ---
class Enemy:
    def __init__(self, enemy_id: str, name: str, sprite_type: str, grid_x: int, grid_y: int, stats: dict, is_boss: bool = False, is_ultimate_boss: bool = False) -> None:
        self.id = enemy_id
        self.name = name
        self.sprite_type = sprite_type  # "yuan_soldier", "yuan_boss", "yuan_emperor"
        self.grid_x = grid_x
        self.grid_y = grid_y
        
        # Pixel coordinates for smooth sliding movement
        self.pixel_x = grid_x * TILE_SIZE
        self.pixel_y = grid_y * TILE_SIZE
        
        self.target_grid_x = grid_x
        self.target_grid_y = grid_y
        
        self.direction = DIR_DOWN
        self.is_moving = False
        self.move_speed = 2  # Slightly slower than player (player is 4) to give player a chance to escape!
        
        # Animation
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 12  # Frames per animation step
        
        # RPG Stats
        self.hp = stats.get("hp", 100)
        self.max_hp = stats.get("hp", 100)
        self.atk = stats.get("atk", 15)
        self.def_val = stats.get("def", 5)  # Avoid using 'def' as it is a python keyword
        self.exp_reward = stats.get("exp_reward", 100)
        
        self.is_boss = is_boss
        self.is_ultimate_boss = is_ultimate_boss
        
        # AI State
        self.ai_state = "wander"
        self.chase_range = 5 if is_boss else 4
        self.move_cooldown = 60  # Frames between moves
        self.wander_chance = 0.2  # 20% chance to move when wandering

    def get_current_sprite_frame(self) -> int:
        if self.anim_frame == 0 or self.anim_frame == 2:
            return 0
        elif self.anim_frame == 1:
            return 1
        else:
            return 2

    def update(self, player_x: int, player_y: int, collision_checker: callable) -> None:
        """Updates enemy position, animation, and AI behavior."""
        if self.is_moving:
            # Move pixel coordinates towards target grid coordinates
            target_pixel_x = self.target_grid_x * TILE_SIZE
            target_pixel_y = self.target_grid_y * TILE_SIZE
            
            if self.pixel_x < target_pixel_x:
                self.pixel_x += self.move_speed
            elif self.pixel_x > target_pixel_x:
                self.pixel_x -= self.move_speed
                
            if self.pixel_y < target_pixel_y:
                self.pixel_y += self.move_speed
            elif self.pixel_y > target_pixel_y:
                self.pixel_y -= self.move_speed
                
            # Check if reached target
            if self.pixel_x == target_pixel_x and self.pixel_y == target_pixel_y:
                self.grid_x = self.target_grid_x
                self.grid_y = self.target_grid_y
                self.is_moving = False
                self.anim_frame = 0  # Reset to standing frame
                self.move_cooldown = 30 if self.ai_state == "chase" else 60  # Reset cooldown
                
            # Cycle walking animation frames
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            self.anim_frame = 0
            if self.move_cooldown > 0:
                self.move_cooldown -= 1
            else:
                self.decide_ai_action(player_x, player_y, collision_checker)

    def decide_ai_action(self, player_x: int, player_y: int, collision_checker: callable) -> None:
        # Calculate Manhattan distance to player
        dist = abs(self.grid_x - player_x) + abs(self.grid_y - player_y)
        
        if dist <= self.chase_range:
            self.ai_state = "chase"
            # Chase player
            dx = player_x - self.grid_x
            dy = player_y - self.grid_y
            
            # Decide which direction to move
            # Try to move in the direction of the larger difference first
            moves = []
            if abs(dx) >= abs(dy):
                moves.append((1 if dx > 0 else -1, 0, DIR_RIGHT if dx > 0 else DIR_LEFT))
                moves.append((0, 1 if dy > 0 else -1, DIR_DOWN if dy > 0 else DIR_UP))
            else:
                moves.append((0, 1 if dy > 0 else -1, DIR_DOWN if dy > 0 else DIR_UP))
                moves.append((1 if dx > 0 else -1, 0, DIR_RIGHT if dx > 0 else DIR_LEFT))
                
            # Try the moves
            moved = False
            for step_x, step_y, direction in moves:
                target_x = self.grid_x + step_x
                target_y = self.grid_y + step_y
                
                # Don't walk onto player's tile directly (adjacent is fine, but entering player tile triggers battle or blocks)
                if target_x == player_x and target_y == player_y:
                    # Adjacent to player, face player
                    self.direction = direction
                    moved = True
                    break
                
                if 0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT:
                    if not collision_checker(target_x, target_y):
                        self.target_grid_x = target_x
                        self.target_grid_y = target_y
                        self.direction = direction
                        self.is_moving = True
                        self.anim_frame = 1
                        self.anim_timer = 0
                        moved = True
                        break
            if not moved:
                # If blocked, wander or stay still
                self.move_cooldown = 20  # Try again soon
        else:
            self.ai_state = "wander"
            # Wander randomly
            import random
            if random.random() < self.wander_chance:
                direction = random.choice([DIR_DOWN, DIR_UP, DIR_LEFT, DIR_RIGHT])
                step_x, step_y = 0, 0
                if direction == DIR_DOWN: step_y = 1
                elif direction == DIR_UP: step_y = -1
                elif direction == DIR_LEFT: step_x = -1
                elif direction == DIR_RIGHT: step_x = 1
                
                target_x = self.grid_x + step_x
                target_y = self.grid_y + step_y
                
                # Check boundaries and obstacles
                if 0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT:
                    if not collision_checker(target_x, target_y) and not (target_x == player_x and target_y == player_y):
                        self.target_grid_x = target_x
                        self.target_grid_y = target_y
                        self.direction = direction
                        self.is_moving = True
                        self.anim_frame = 1
                        self.anim_timer = 0
                
                self.move_cooldown = random.randint(40, 80)
            else:
                self.move_cooldown = random.randint(20, 40)

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int, sprites: dict[str, dict[str, list[pygame.Surface]]]) -> None:
        frame_idx = self.get_current_sprite_frame()
        
        # Fetch sprite
        if self.sprite_type in sprites and self.direction in sprites[self.sprite_type]:
            sprite = sprites[self.sprite_type][self.direction][frame_idx]
        else:
            # Fallback
            return
            
        screen_pos_x = self.pixel_x - camera_x
        screen_pos_y = self.pixel_y - camera_y
        
        # Handle larger sizes for Bosses
        if self.is_ultimate_boss:
            # 2.0x scale (128x128)
            scaled_sprite = pygame.transform.scale(sprite, (TILE_SIZE * 2, TILE_SIZE * 2))
            # Center the larger sprite on the tile
            offset_x = -TILE_SIZE // 2
            offset_y = -TILE_SIZE
            surface.blit(scaled_sprite, (screen_pos_x + offset_x, screen_pos_y + offset_y))
        elif self.is_boss:
            # 1.5x scale (96x96)
            scaled_sprite = pygame.transform.scale(sprite, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 1.5)))
            # Center the larger sprite on the tile
            offset_x = -TILE_SIZE // 4
            offset_y = -TILE_SIZE // 2
            surface.blit(scaled_sprite, (screen_pos_x + offset_x, screen_pos_y + offset_y))
        else:
            surface.blit(sprite, (screen_pos_x, screen_pos_y))

# --- Game Class ---
class Game:
    def __init__(self) -> None:
        # First, beautify and update all dynamic maps on startup
        self.beautify_and_update_all_maps()
        
        self.assets = AssetManager()
        self.current_map_id = "north"
        self.player = Player(13, 5)  # Start right in front of Zhu's home
        self.state = STATE_NORMAL
        self.talked_npcs: set[str] = set()
        
        # Load Equipment Table in GBK encoding
        self.equipment_table: dict[str, list[dict]] = {}
        self.load_equipment_table()
        
        # Equip stats cache for fast attack/defense lookup
        self.cache_equipment_stats()
        
        # Dropped/Reward equipment decision state
        self.dropped_equip: dict | None = None
        self.dropped_slot: str | None = None
        self.choice_start_time: int = 0
        self.chopping_start_time: int | None = None
        
        # Battle system state
        self.battle_start_time: int | None = None
        self.battle_monster_id: str | None = None
        self.battle_cooldown_timer: int = 0
        self.monster_table: dict[str, dict] = {}
        self.load_monster_table()
        
        # Enemy system state
        self.enemies: list[Enemy] = []
        self.battle_enemy: Enemy | None = None
        self.spawn_enemies_for_current_map()
        
        # Dialogue system state
        self.dialogue_lines: list[str] = []
        self.dialogue_index = 0
        self.dialogue_text = ""
        self.dialogue_char_index = 0
        self.dialogue_speaker = ""
        self.dialogue_timer = 0
        self.dialogue_speed = 1  # Characters per frame
        
        # Story system state
        self.visited_scenes: set[str] = set()
        self.scene_stories: dict[str, str] = {}
        self.story_text = ""
        self.story_char_index = 0
        self.story_timer = 0
        self.story_speed = 1  # Characters per frame
        self.load_scene_stories()
        
        # Load fonts
        self.font_title = self.get_chinese_font(24)
        self.font_ui = self.get_chinese_font(18)
        self.font_dialogue = self.get_chinese_font(20)
        self.font_small = self.get_chinese_font(14)

    def beautify_and_update_all_maps(self) -> None:
        """Beautifies all dynamic scene maps and updates their min_levels on disk and in memory."""
        import random
        from map_data import MAPS
        
        scenes_dir = BASE_DIR / "assets" / "scenes"
        flag_file = BASE_DIR / "assets" / ".maps_beautified"
        
        scene_levels = {
            "huangjuesi": 1,
            "huaixi": 2,
            "henan": 3,
            "miaoshan": 4,
            "lvpaizhai": 5,
            "hezhou": 6,
            "taiping": 7,
            "yingtian": 8,
            "huizhou": 9,
            "zhedong": 10,
            "jinhua": 11,
            "poyanghu": 12,
            "suzhou": 13,
            "yuandadu": 14,
            "sichuan": 15,
            "yunnan": 16
        }
        
        # Always update min_levels in memory first to ensure drop quality is correct immediately
        for scene_id, level in scene_levels.items():
            if scene_id in MAPS:
                MAPS[scene_id]["min_level"] = level
                
        # If already beautified on disk, skip disk write to preserve performance and manual edits
        if flag_file.exists():
            return
            
        if not scenes_dir.exists():
            return
            
        print("Beautifying all dynamic maps...")
        for path in scenes_dir.glob("*.json"):
            scene_id = path.stem
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Update level
                level = scene_levels.get(scene_id, 1)
                data["min_level"] = level
                
                # Skip beautifying huangjuesi since it's already manually beautified
                if scene_id != "huangjuesi":
                    ground = [list(row) for row in data["ground"]]
                    obstacle = [list(row) for row in data["obstacle"]]
                    
                    H = len(ground)
                    W = len(ground[0])
                    
                    # Keep clear coordinates
                    clear_coords = set()
                    for npc in data.get("npcs", []):
                        nx, ny = npc["x"], npc["y"]
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                if 0 <= ny + dy < H and 0 <= nx + dx < W:
                                    clear_coords.add((nx + dx, ny + dy))
                                    
                    for chest in data.get("chests", []):
                        cx, cy = chest["x"], chest["y"]
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                if 0 <= cy + dy < H and 0 <= cx + dx < W:
                                    clear_coords.add((cx + dx, cy + dy))
                                    
                    for y in range(H):
                        for x in range(W):
                            g_char = ground[y][x]
                            if g_char in ['r', 'w', 'b', 'o', 'a', 'd', 'v']:
                                clear_coords.add((x, y))
                                for dy in [-1, 0, 1]:
                                    for dx in [-1, 0, 1]:
                                        if 0 <= y + dy < H and 0 <= x + dx < W:
                                            clear_coords.add((x + dx, y + dy))
                                            
                    # Beautify Ground
                    for y in range(H):
                        for x in range(W):
                            if (x, y) in clear_coords:
                                continue
                            g_char = ground[y][x]
                            if g_char == 'g':
                                r = random.random()
                                if r < 0.08: ground[y][x] = 'f'
                                elif r < 0.13: ground[y][x] = 's'
                                elif r < 0.18: ground[y][x] = 'h'
                            elif g_char == 'h':
                                r = random.random()
                                if r < 0.10: ground[y][x] = 's'
                                elif r < 0.15: ground[y][x] = 'g'
                                
                    # Beautify Obstacles
                    for y in range(1, H - 1):
                        for x in range(1, W - 1):
                            if (x, y) in clear_coords:
                                continue
                            if obstacle[y][x] != '.':
                                continue
                            r = random.random()
                            if "huaixi" in scene_id:
                                if r < 0.03: obstacle[y][x] = 'K'
                                elif r < 0.05: obstacle[y][x] = 'F'
                                elif r < 0.07: obstacle[y][x] = 'v'
                                elif r < 0.09: obstacle[y][x] = 'T'
                            elif "henan" in scene_id:
                                if r < 0.04: obstacle[y][x] = 'K'
                                elif r < 0.07: obstacle[y][x] = 'Y'
                            elif "miaoshan" in scene_id:
                                if r < 0.06: obstacle[y][x] = 'P'
                                elif r < 0.10: obstacle[y][x] = 'T'
                            elif "lvpaizhai" in scene_id:
                                if r < 0.03: obstacle[y][x] = 'F'
                                elif r < 0.05: obstacle[y][x] = 'B'
                                elif r < 0.07: obstacle[y][x] = 'U'
                                elif r < 0.08: obstacle[y][x] = 'X'
                            elif "hezhou" in scene_id:
                                if r < 0.03: obstacle[y][x] = 'U'
                                elif r < 0.05: obstacle[y][x] = 'F'
                                elif r < 0.07: obstacle[y][x] = 'X'
                                elif r < 0.09: obstacle[y][x] = 'T'
                            elif "taiping" in scene_id or "yingtian" in scene_id or "yuandadu" in scene_id:
                                if r < 0.02: obstacle[y][x] = 'J'
                                elif r < 0.04: obstacle[y][x] = 'F'
                                elif r < 0.06: obstacle[y][x] = 'U'
                                elif r < 0.08: obstacle[y][x] = 'S'
                                elif r < 0.10: obstacle[y][x] = 'R'
                                elif r < 0.12: obstacle[y][x] = 'W'
                            elif "huizhou" in scene_id:
                                if r < 0.04: obstacle[y][x] = 'M'
                                elif r < 0.06: obstacle[y][x] = 'J'
                                elif r < 0.08: obstacle[y][x] = 'R'
                                elif r < 0.10: obstacle[y][x] = 'W'
                            elif "zhedong" in scene_id:
                                if r < 0.04: obstacle[y][x] = 'M'
                                elif r < 0.07: obstacle[y][x] = 'T'
                                elif r < 0.09: obstacle[y][x] = 'F'
                                elif r < 0.11: obstacle[y][x] = 'v'
                            elif "jinhua" in scene_id:
                                if r < 0.05: obstacle[y][x] = 'm'
                                elif r < 0.09: obstacle[y][x] = 'i'
                                elif r < 0.12: obstacle[y][x] = 'v'
                                elif r < 0.14: obstacle[y][x] = 'F'
                                elif r < 0.15: obstacle[y][x] = 'J'
                            elif "poyanghu" in scene_id:
                                if r < 0.03: obstacle[y][x] = 'T'
                                elif r < 0.05: obstacle[y][x] = 'P'
                            elif "suzhou" in scene_id:
                                if r < 0.03: obstacle[y][x] = 'R'
                                elif r < 0.06: obstacle[y][x] = 'W'
                                elif r < 0.08: obstacle[y][x] = 'J'
                                elif r < 0.10: obstacle[y][x] = 'F'
                            elif "sichuan" in scene_id:
                                if r < 0.04: obstacle[y][x] = 'P'
                                elif r < 0.07: obstacle[y][x] = 'K'
                                elif r < 0.09: obstacle[y][x] = 'm'
                            elif "yunnan" in scene_id:
                                if r < 0.05: obstacle[y][x] = 'M'
                                elif r < 0.08: obstacle[y][x] = 'Y'
                                
                    data["ground"] = ["".join(row) for row in ground]
                    data["obstacle"] = ["".join(row) for row in obstacle]
                    
                # Save back to disk
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                # Update in memory representation
                if scene_id in MAPS:
                    MAPS[scene_id]["ground"] = data["ground"]
                    MAPS[scene_id]["obstacle"] = data["obstacle"]
                    MAPS[scene_id]["min_level"] = level
                    
            except Exception as e:
                print(f"Error beautifying scene {scene_id}: {e}")
                
        # Write flag file
        try:
            with open(flag_file, "w") as f:
                f.write("beautified")
            print("Successfully beautified all dynamic maps!")
        except Exception as e:
            print(f"Error writing flag file: {e}")

    def load_scene_stories(self) -> None:
        """Loads scene stories from assets/scene_stories.json. Auto-generates it in GBK if missing."""
        json_path = BASE_DIR / "assets" / "scene_stories.json"
        
        # Default stories dictionary to write if missing
        default_stories = {
            "north": "至正四年（1344年），濠州大旱，蝗灾与瘟疫横行。朱重八（朱元璋）眼睁睁看着父母与长兄在几天内相继饿死病死。家里无立锥之地，连安葬父母的棺木都没有。在这绝望的时刻，邻里刘继祖施舍了一块坟地，重八才得以用破衣裹尸安葬了亲人。为了活命，十七岁的重八决定告别这片伤心之地，前往不远处的皇觉寺投奔剃度，当一个行童和尚。乱世求生，开局一个碗，大明的传奇便从这碗开始。",
            "south": "至正四年秋，朱重八怀着无比沉重的心情，在钟离县南的大地上徘徊。放眼望去，田地龟裂，寸草不生，到处都是流离失所的饥民和累累白骨。重八在父母的坟前长跪不起，重重地叩了三个响头。他知道，如果继续留在这里，等待他的只有死路一条。他擦干眼泪，紧紧攥着行囊，踏上了未知的道路。这片生他养他的土地，如今已被元朝的暴政和天灾摧毁殆尽，唯有走出去，才能寻得一线生机。",
            "huangjuesi": "至正四年，朱重八进入皇觉寺，剃度为僧。在这里，他只是个地位低下的行童，每天要扫地、挑水、烧香、撞钟，稍有不慎便会遭到老和尚的打骂。然而，好景不长，饥荒很快蔓延到了寺庙，寺里也无米下锅。主持大师无奈之下，发给重八和众僧每人一个破木碗，让他们下山化缘。重八看着手中的破碗，百感交集。他再次被推向了风雨飘摇的乱世，但正是这只破碗，将伴随他走过千山万水，最终打下大明的锦绣江山。",
            "huaixi": "至正四年至至正八年（1344-1348年），朱重八手持破碗，在淮西平原上开始了长达四年的流浪乞讨生涯。他走遍了淮西的荒村野岭，风餐露宿，历尽人间冷暖。在这期间，他亲眼目睹了元朝官吏对百姓的残酷剥削，也结识了无数同样挣扎在生死边缘的底层穷人。淮西的苦难没有压垮他，反而磨砺了他坚韧不拔的意志，让他深刻理解了民心所向。这段看似卑微的乞讨经历，成为了他日后起兵反元最宝贵的精神财富。",
            "henan": "至正八年，朱重八的足迹踏上了河南大地。此时的黄河连年决口，百姓流离失所，而元廷不仅不加赈灾，反而强征民夫修筑河道，致使怨声载道。重八在河南看到了白莲教和红巾军起义的火种正在暗中酝酿，‘石人一只眼，挑动黄河天下反’的民谣在民间悄然流传。他敏锐地意识到，这个腐朽的元帝国已经走到了尽头，天下即将大乱。他决定结束流浪，返回皇觉寺，静待风云变幻的那一天。",
            "miaoshan": "至正十二年（1352年），朱元璋已投奔濠州红巾军郭子兴部，因作战勇敢、智勇双全，深受器重。为了扩大实力，朱元璋主动请缨，前往定远妙山招募新兵。妙山地势险要，聚集了大量因逃避战乱而进山避难的强壮乡民。朱元璋凭借着真诚的态度和卓越的领袖魅力，宣扬‘驱逐胡虏，恢复中华’的救世大义，成功感召了妙山数百名热血青年投军。这支妙山新兵，成为了朱元璋真正拥有的第一支嫡系武装力量。",
            "lvpaizhai": "至正十三年，朱元璋率军进驻定远驴牌寨。此时的驴牌寨聚集了三千多名地方武装，他们虽然人数众多，但缺乏统一的指挥和充足的粮饷，正处于进退两难的境地。朱元璋单骑入寨，面见寨主，陈说天下大势，晓以利害。他指出偏安一隅终将覆灭，唯有加入红巾军共图大业，方能建功立业。寨主被朱元璋的胆识与诚意折服，率领三千好汉全部归顺。朱元璋不费一兵一卒，实力大增，反元大业初具规模。",
            "hezhou": "至正十五年（1355年），朱元璋被任命为和州总兵。和州紧邻长江，是连接江淮与江南的战略要地。朱元璋在此屯兵积粮，严明军纪，深受和州百姓的拥戴。此时，数万大军已在和州渡口集结完毕，战船遮天蔽日。朱元璋伫立江边，望着滚滚东逝的长江水，心中豪情万丈。长江天险虽固，但也挡不住红巾军渡江南下的铁蹄。攻克江南，夺取金陵，建立帝王之基的宏伟蓝图，即将在和州渡口拉开序幕。",
            "taiping": "至正十五年秋，朱元璋率军横渡长江，一举攻克太平府。进城后，朱元璋严令部下‘秋毫无犯’，严禁抢掠百姓，并开仓放粮，救济饥民。这一仁义之举与残暴的元军形成了鲜明对比，太平府的名士儒生 and 黎民百姓无不箪食壶浆，夹道欢迎王师。在这里，朱元璋不仅赢得了民心，还招揽了大量治国理政的优秀人才。太平府的和平占领，标志着朱元璋的军队正式从一支农民起义军，转变为有纪律、有抱负的仁义之师。",
            "yingtian": "至正十六年（1356年），朱元璋攻占集庆，改名应天府（今南京），以此为大本营。应天虎踞龙盘，依山带江，乃帝王之基。在这里，朱元璋亲自登门拜访了隐居的绝世贤才刘伯温。刘伯温为朱元璋献上了平定天下的战略宏图，并极力推行‘高筑墙，广积粮，缓称王’的九字国策。朱元璋深以为然，在应天大力发展农业，修筑坚固城墙，暗中积蓄力量。应天府，成为了朱元璋席卷天下、开创大明帝国的最强基石。",
            "huizhou": "至正十七年，朱元璋麾下大军攻占徽州。徽州山川险固，自古便是文风昌盛、商贸繁荣之地。在这里，隐居的徽州名士朱升向朱元璋提出了著名的建言。朱元璋采纳其策，在徽州轻徭薄赋，屯兵积粮，使徽州成为了应天府最稳固的后方粮仓。徽州淳朴的民风和丰饶的物产，为朱元璋提供了源源不断的兵源和军饷，让他无后顾之忧，得以全力应对西面陈友谅和东面张士诚的巨大威胁。",
            "zhedong": "至正十八年，朱元璋挥师东进，平定浙东地区。浙东自古多才俊，是江南文化的中心。朱元璋在此展现了对知识分子的极高尊重，亲自迎请了以刘基（刘伯温）、宋濂、章溢、叶琛为首的‘浙东四先生’。这些顶尖智囊的加入，彻底改变了朱元璋集团的知识结构，为他制定了极其严密的政治、军事和法律制度。浙东的收复，不仅扩大了统治疆域，更在精神 and 舆论上确立了朱元璋作为华夏正统继承者的地位。",
            "jinhua": "至正十八年冬，朱元璋亲临金华。金华百姓久闻朱帅仁义之名，纷纷出城迎接。当地农夫更是献上了金华特产的火腿，香气四溢，用以慰劳抗元将士。朱元璋大喜，将其作为军粮推广。在金华，朱元璋整顿吏治，兴修水利，鼓励耕织，使饱受战火摧残的江南农村迅速恢复了生机。金华的稳定与繁荣，向天下昭示了朱元璋不仅能征善战，更有治国安民之能，赢得了江南士绅与庶民的广泛归心。",
            "poyanghu": "至正二十三年（1363年），震惊历史的鄱阳湖大决战爆发。朱元璋率领二十万大军，与号称六十万大军的汉王陈友谅在鄱阳湖展开了生死对决。陈友谅的巨型楼船遮天蔽日，犹如水上长城；朱元璋的战船则矮小灵活。面对前所未有的强敌，大将韩成因相貌酷似朱元璋，在危急关头穿上金甲代主投江，以稳定军心。朱元璋抓住战机，利用火攻火烧连营，最终击杀陈友谅，取得了中国历史上最大规模水战的辉煌胜利。",
            "suzhou": "至正二十七年（1367年），在消灭了西面的陈友谅后，朱元璋调集大军，合围东吴张士诚的大本营——苏州。苏州城防坚固，张士诚深得民心，誓死抵抗。朱元璋采取‘筑长围以困之’的战略，进行了长达数月的艰苦围城战。最终，明军攻破姑苏城，张士诚自缢未遂被俘。苏州的攻克，彻底扫平了江南的割据势力，江南富庶之地尽归朱元璋所有。至此，南方统一大业圆满完成，北伐中原的号角即将吹响。",
            "yuandadu": "洪武元年（1368年），朱元璋在应天府奉天殿即皇帝位，建国号大明，建元洪武。随后，他命大将军徐达、副将军常遇春率二十万大军挥师北伐。明军势如破竹，直指元朝首都元大都。元顺帝见大势已去，连夜率嫔妃臣子北逃漠北。徐达率军顺利攻克元大都，改名北平。至此，统治中原百余年的元朝宣告灭亡，丢失四百余年的燕云十六州重新收复。百年胡运，一朝而终，华夏重归太平！",
            "sichuan": "洪武四年（1371年），大明帝国刚刚建立，天下初定。为了实现天下一统，朱元璋派遣大军分兵两路，入川平定割据四川的明夏政权。蜀道虽难，难挡大明王师。明军纪律严明，所到之处秋毫无犯，蜀中父老纷纷开城归顺。四川的和平收复，不仅消灭了西南的最大割据势力，更将天府之国的富庶物产与险要地势纳入大明版图，使大明帝国的西南大后方坚如磐石，万世基业再添保障。",
            "yunnan": "洪武十四年（1381年），大明开国已过十余载，但退守云南的元朝梁王势力依然负愚顽抗。朱元璋派遣大将傅友德、蓝玉、沐英率三十万大军远征云南。大军翻山越岭，荡平梁王余孽，收复云南全境。大将沐英因战功卓著，且忠心耿耿，被朱元璋委以重任，世代镇守云南。沐英不负重托，在云南兴修水利、屯田开荒、传播华夏文化，使西南边疆永固。至此，大明一统乾坤，海内升平，万世太平！"
        }
        
        if not json_path.exists():
            try:
                json_str = json.dumps(default_stories, ensure_ascii=False, indent=2)
                with open(json_path, "w", encoding="gbk") as f:
                    f.write(json_str)
                print("Created assets/scene_stories.json in GBK!")
            except Exception as e:
                print(f"Error creating assets/scene_stories.json: {e}")
                
        # Load the stories
        try:
            with open(json_path, "r", encoding="gbk") as f:
                self.scene_stories = json.load(f)
                print("Loaded scene stories in GBK!")
        except Exception as e_gbk:
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self.scene_stories = json.load(f)
                    print("Loaded scene stories in UTF-8!")
            except Exception as e_utf8:
                print(f"Error loading scene stories (GBK): {e_gbk}")
                print(f"Error loading scene stories (UTF-8): {e_utf8}")
                self.scene_stories = default_stories

    def trigger_story(self, map_id: str) -> None:
        """Triggers the first-time story for a scene if not visited yet."""
        if map_id not in self.visited_scenes:
            self.visited_scenes.add(map_id)
            story_content = self.scene_stories.get(map_id)
            if story_content:
                self.state = STATE_STORY
                self.story_text = ""
                self.story_char_index = 0
                self.story_timer = 0
                self.story_lines = [story_content]
                self.story_index = 0
                play_beep(300, 200, 0.2)

    def update_story(self) -> None:
        """Updates the typewriter effect for the story text."""
        current_story = self.story_lines[self.story_index]
        if self.story_char_index < len(current_story):
            self.story_timer += 1
            if self.story_timer >= self.story_speed:
                self.story_timer = 0
                self.story_char_index += 1
                self.story_text = current_story[:self.story_char_index]
                if self.story_char_index % 3 == 0:
                    play_beep(250, 15, 0.03)

    def advance_story(self) -> None:
        """Advances or ends the story screen."""
        current_story = self.story_lines[self.story_index]
        if self.story_char_index < len(current_story):
            # Instant complete
            self.story_char_index = len(current_story)
            self.story_text = current_story
            play_beep(350, 30, 0.05)
        else:
            # End story
            self.state = STATE_NORMAL
            play_beep(400, 60, 0.08)

    def load_equipment_table(self) -> None:
        """Loads static equipment registry from assets."""
        json_path = BASE_DIR / "assets" / "equipment_table.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self.equipment_table = json.load(f)
                    print("Loaded equipment table in UTF-8!")
            except Exception as e_utf8:
                try:
                    with open(json_path, "r", encoding="gbk") as f:
                        self.equipment_table = json.load(f)
                        print("Loaded equipment table in GBK!")
                except Exception as e_gbk:
                    print(f"Error loading equipment table (UTF-8): {e_utf8}")
                    print(f"Error loading equipment table (GBK): {e_gbk}")
        else:
            print("Warning: assets/equipment_table.json not found!")

    def load_monster_table(self) -> None:
        """Loads monster table from assets, auto-creating it in GBK if missing."""
        json_path = BASE_DIR / "assets" / "monster_table.json"
        if not json_path.exists():
            # Auto-create in GBK
            data = {
                "wolf": {
                    "name": "野狼",
                    "atk": 15,
                    "def": 5,
                    "hp": 80,
                    "sprite": "wolf",
                    "exp_reward": 150
                },
                "tiger": {
                    "name": "猛虎",
                    "atk": 35,
                    "def": 15,
                    "hp": 200,
                    "sprite": "tiger",
                    "exp_reward": 400
                },
                "lion": {
                    "name": "狂狮",
                    "atk": 60,
                    "def": 30,
                    "hp": 350,
                    "sprite": "lion",
                    "exp_reward": 800
                }
            }
            try:
                with open(json_path, "w", encoding="gbk") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("Created assets/monster_table.json in GBK!")
            except Exception as e:
                print(f"Error creating monster table: {e}")
                
        # Now load it
        self.monster_table = {}
        if json_path.exists():
            try:
                # Try GBK first as requested
                with open(json_path, "r", encoding="gbk") as f:
                    self.monster_table = json.load(f)
                    print("Loaded monster table in GBK!")
            except Exception as e_gbk:
                try:
                    # Fallback to UTF-8
                    with open(json_path, "r", encoding="utf-8") as f:
                        self.monster_table = json.load(f)
                        print("Loaded monster table in UTF-8!")
                except Exception as e_utf8:
                    print(f"Error loading monster table (GBK): {e_gbk}")
                    print(f"Error loading monster table (UTF-8): {e_utf8}")

    def simulate_battle(self, monster_sprite: str | None, enemy: Enemy | None = None) -> tuple[bool, list[str]]:
        """Simulates a turn-based battle between player and monster/enemy. Returns (win_or_loss, battle_log)."""
        if enemy:
            m_name = enemy.name
            m_hp = enemy.hp
            m_atk = enemy.atk
            m_def = enemy.def_val
            exp_reward = enemy.exp_reward
        else:
            monster = self.monster_table.get(monster_sprite)
            if not monster:
                return False, ["未找到怪物数据。"]
            m_name = monster["name"]
            m_hp = monster["hp"]
            m_atk = monster["atk"]
            m_def = monster["def"]
            exp_reward = monster["exp_reward"]
            
        p_hp = self.player.max_hp  # Start battle with full HP for fairness
        p_atk = self.player.attack
        p_def = self.player.defense
        
        log = [f"⚔️ 开始与【{m_name}】进行决战！"]
        
        # Turn simulation
        round_num = 1
        while p_hp > 0 and m_hp > 0 and round_num <= 50:
            # Player attacks monster
            p_dmg = max(1, p_atk - m_def)
            m_hp -= p_dmg
            log.append(f"第 {round_num} 回合: 你对【{m_name}】造成了 {p_dmg} 点伤害！(敌余HP: {max(0, m_hp)})")
            if m_hp <= 0:
                break
                
            # Monster attacks player
            m_dmg = max(1, m_atk - p_def)
            p_hp -= m_dmg
            log.append(f"第 {round_num} 回合: 【{m_name}】对你造成了 {m_dmg} 点伤害！(自余HP: {max(0, p_hp)})")
            if p_hp <= 0:
                break
                
            round_num += 1
            
        if m_hp <= 0:
            return True, log
        else:
            return False, log

    def get_near_monster(self) -> dict | None:
        """Returns the adjacent monster NPC if any."""
        map_data = MAPS.get(self.current_map_id)
        if not map_data:
            return None
        npcs = map_data.get("npcs", [])
        px, py = self.player.grid_x, self.player.grid_y
        for npc in npcs:
            sprite_id = npc.get("sprite")
            if sprite_id in self.monster_table:
                # Check if adjacent (distance <= 1 diagonally too)
                if abs(npc["x"] - px) <= 1 and abs(npc["y"] - py) <= 1:
                    return npc
        return None

    def get_near_enemy(self) -> Enemy | None:
        """Returns an adjacent active Enemy if any."""
        px, py = self.player.grid_x, self.player.grid_y
        for enemy in self.enemies:
            # Check if adjacent (distance <= 1 diagonally too)
            if abs(enemy.grid_x - px) <= 1 and abs(enemy.grid_y - py) <= 1:
                return enemy
        return None

    def remove_monster_npc(self, npc_id: str) -> None:
        """Removes a defeated monster NPC from the current map."""
        map_data = MAPS.get(self.current_map_id)
        if map_data and "npcs" in map_data:
            map_data["npcs"] = [npc for npc in map_data["npcs"] if npc.get("id") != npc_id]

    def cache_equipment_stats(self) -> None:
        """Builds flat caches for Player class to lookup atk/def bonuses quickly."""
        atk_cache = {}
        def_cache = {}
        for slot, items in self.equipment_table.items():
            for item in items:
                name = item["name"]
                atk_cache[name] = item.get("atk", 0)
                def_cache[name] = item.get("def", 0)
                
        # Inject onto player instance
        self.player.loaded_atk_stats = atk_cache
        self.player.loaded_def_stats = def_cache

    def roll_random_equipment_drop(self) -> None:
        """Rolls a random slot, pulls a random item, and enters equipment choice screen."""
        import random
        if not self.equipment_table:
            return
            
        # Select random slot
        slots = list(self.equipment_table.keys())
        self.dropped_slot = random.choice(slots)
        
        # Select random item from that slot
        items_list = self.equipment_table[self.dropped_slot]
        
        # Get map min_level to bound quality
        map_info = MAPS.get(self.current_map_id, {})
        min_level = map_info.get("min_level", 1)
        
        # Determine allowed qualities based on map min_level
        # Level 1: "白" only
        # Level 2: "白", "绿"
        # Level 3: "白", "绿", "蓝"
        # Level 4-5: "白", "绿", "蓝", "紫"
        # Level 6+: "白", "绿", "蓝", "紫", "橙"
        allowed_qualities = ["白"]
        if min_level >= 2:
            allowed_qualities.append("绿")
        if min_level >= 3:
            allowed_qualities.append("蓝")
        if min_level >= 4:
            allowed_qualities.append("紫")
        if min_level >= 6:
            allowed_qualities.append("橙")
            
        # Filter items matching allowed qualities
        filtered_items = [it for it in items_list if it.get("quality", "白") in allowed_qualities]
        if not filtered_items:
            filtered_items = [it for it in items_list if it.get("quality") == "白"]
            
        self.dropped_equip = random.choice(filtered_items)
        
        # Change state and play chime
        self.state = STATE_EQUIP_CHOICE
        self.choice_start_time = pygame.time.get_ticks()
        play_chime_success()

    def confirm_equip_replace(self) -> None:
        """Replaces current slot with dropped equipment."""
        if self.dropped_slot and self.dropped_equip:
            new_item_name = self.dropped_equip["name"]
            
            # Place in equipment
            self.player.equipment[self.dropped_slot] = new_item_name
            if new_item_name not in self.player.inventory:
                self.player.inventory.append(new_item_name)
                
            # Alert dialog
            self.state = STATE_DIALOGUE
            msg = [
                f"成功装备【{new_item_name}】至【{self.dropped_slot}】部位！",
                f"属性获得同步刷新。"
            ]
            self.start_dialogue("系统", msg)
            play_chime_success()
            
            # Clear drop state
            self.dropped_slot = None
            self.dropped_equip = None

    def discard_equip_drop(self) -> None:
        """Discards dropped equipment."""
        if self.dropped_equip:
            discard_name = self.dropped_equip["name"]
            self.state = STATE_DIALOGUE
            self.start_dialogue("系统", [f"你随手丢弃了【{discard_name}】。"])
            play_beep(250, 100, 0.08)
            
            # Clear drop state
            self.dropped_slot = None
            self.dropped_equip = None

    def compare_and_decide_equip(self) -> None:
        """Compares current and dropped equipment quality and auto-decides."""
        if not self.dropped_equip or not self.dropped_slot:
            return
            
        # Quality mapping
        quality_map = {"白": 0, "绿": 1, "蓝": 2, "紫": 3, "橙": 4}
        
        # Get dropped equipment quality
        drop_quality = self.dropped_equip.get("quality", "白")
        drop_val = quality_map.get(drop_quality, 0)
        
        # Get current equipment quality
        curr_item_name = self.player.equipment.get(self.dropped_slot)
        curr_val = -1 # If empty slot, dropped is always better
        
        if curr_item_name:
            curr_item_quality = "白"
            found = False
            for slot, items in self.equipment_table.items():
                for it in items:
                    if it["name"] == curr_item_name:
                        curr_item_quality = it.get("quality", "白")
                        found = True
                        break
                if found:
                    break
            curr_val = quality_map.get(curr_item_quality, 0)
            
        if drop_val > curr_val:
            # Better quality -> Replace
            self.confirm_equip_replace()
        else:
            # Worse or equal quality -> Discard
            self.discard_equip_drop()

    def is_tree_at(self, x: int, y: int) -> bool:
        """Checks if there is a tree obstacle at (x, y)."""
        map_data = MAPS.get(self.current_map_id)
        if not map_data:
            return False
        obstacle_map = map_data["obstacle"]
        if 0 <= y < len(obstacle_map) and 0 <= x < len(obstacle_map[0]):
            char = obstacle_map[y][x]
            return char in ['T', 'P', 'M', 'K']
        return False

    def is_near_tree(self) -> bool:
        """Checks if the player is adjacent (including diagonally) to any tree tile."""
        px, py = self.player.grid_x, self.player.grid_y
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if self.is_tree_at(px + dx, py + dy):
                    return True
        return False

    def get_chinese_font(self, size: int) -> pygame.font.Font:
        """Finds a system font that supports Chinese characters, falls back to default."""
        system_fonts = ["microsoftyahei", "simhei", "simsun", "stxihei", "dengxian"]
        for font_name in system_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                if font:
                    return font
            except Exception:
                continue
        return pygame.font.Font(None, size)

    def is_tile_solid(self, x: int, y: int) -> bool:
        """Determines if a tile at (x, y) is solid and blocks movement."""
        map_data = MAPS[self.current_map_id]
        ground_map = map_data["ground"]
        obstacle_map = map_data["obstacle"]
        npcs = map_data["npcs"]
        
        # 1. Check ground layer (water is solid unless it's a bridge)
        ground_char = ground_map[y][x]
        if ground_char in ['w', 'o', 'd']:  # Calm water, wavy water, deep water
            if ground_char == 'b':
                return False
            return True
            
        # 2. Check obstacle layer
        obstacle_char = obstacle_map[y][x]
        # Walkable characters on Layer 1: '.' (empty), 'm' (wheat), 'i' (rice), 'v' (vegetables), 'D' (door)
        if obstacle_char != '.' and obstacle_char not in ['m', 'i', 'v', 'D']:
            return True
            
        # 3. Check NPCs
        for npc in npcs:
            if npc["x"] == x and npc["y"] == y:
                return True
                
        return False

    def is_tile_solid_for_enemy(self, x: int, y: int, ignore_enemy_id: str = None) -> bool:
        """Checks if a tile is solid for an enemy (includes obstacles, NPCs, and other enemies)."""
        # First, check standard solid tiles
        if self.is_tile_solid(x, y):
            return True
            
        # Also check other enemies
        for enemy in self.enemies:
            if enemy.id == ignore_enemy_id:
                continue
            if enemy.grid_x == x and enemy.grid_y == y:
                return True
            if enemy.target_grid_x == x and enemy.target_grid_y == y:
                return True
                
        return False

    def spawn_enemies_for_current_map(self) -> None:
        """Spawns random enemies and a scene boss for the current map."""
        self.enemies = []
        
        # Don't spawn in the very first map (north) to let player learn
        if self.current_map_id == "north":
            return
            
        map_data = MAPS.get(self.current_map_id)
        if not map_data:
            return
            
        min_level = map_data.get("min_level", 1)
        
        # Determine number of soldiers to spawn
        import random
        num_soldiers = random.randint(3, 5)
        if self.current_map_id == "south":
            num_soldiers = 2  # Fewer on south map
            
        # Find walkable tiles
        walkable_tiles = []
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                # Don't spawn too close to the player's starting position
                dist_to_player = abs(x - self.player.grid_x) + abs(y - self.player.grid_y)
                if dist_to_player > 5 and not self.is_tile_solid(x, y):
                    walkable_tiles.append((x, y))
                    
        if not walkable_tiles:
            return
            
        # 1. Spawn Soldiers
        random.shuffle(walkable_tiles)
        for i in range(min(num_soldiers, len(walkable_tiles))):
            x, y = walkable_tiles.pop()
            
            soldier_stats = {
                "hp": min_level * 40 + 60,
                "atk": min_level * 8 + 12,
                "def": min_level * 4 + 4,
                "exp_reward": min_level * 80 + 40
            }
            
            # Soldier names
            soldier_names = ["元军步兵", "元军弓箭手", "元军刀盾兵", "元军骑兵"]
            name = random.choice(soldier_names)
            
            soldier = Enemy(
                enemy_id=f"soldier_{self.current_map_id}_{i}",
                name=name,
                sprite_type="yuan_soldier",
                grid_x=x,
                grid_y=y,
                stats=soldier_stats
            )
            self.enemies.append(soldier)
            
        # 2. Spawn Boss
        boss_names = {
            "south": "元军哨长·哈剌不花",
            "huangjuesi": "元军监军·脱脱木儿",
            "huaixi": "元军百户·答失八都鲁",
            "henan": "元军千户·阿鲁温",
            "miaoshan": "元军先锋·也先帖木儿",
            "lvpaizhai": "元军副将·贾鲁",
            "hezhou": "元军提控·陈野先",
            "taiping": "元军元帅·蛮子海牙",
            "yingtian": "元军守将·福寿",
            "huizhou": "元军总管·达识帖木儿",
            "zhedong": "元军平章·石末宜孙",
            "jinhua": "元军万户·忽都帖木儿",
            "poyanghu": "元军水师提督·也先不花",
            "suzhou": "元军大将·孛罗帖木儿",
            "sichuan": "元军大将·完者帖木儿",
            "yunnan": "梁王·把匝剌瓦尔密",
            "yuandadu": "元顺帝·妥欢贴睦尔" # Ultimate Boss!
        }
        
        if walkable_tiles:
            x, y = walkable_tiles.pop()
            
            is_ultimate = (self.current_map_id == "yuandadu")
            boss_name = boss_names.get(self.current_map_id, "元军守将")
            
            if is_ultimate:
                # Ultimate Boss stats
                boss_stats = {
                    "hp": 5000,
                    "atk": 500,
                    "def": 250,
                    "exp_reward": 10000
                }
                boss = Enemy(
                    enemy_id=f"boss_{self.current_map_id}",
                    name=boss_name,
                    sprite_type="yuan_emperor",
                    grid_x=x,
                    grid_y=y,
                    stats=boss_stats,
                    is_boss=True,
                    is_ultimate_boss=True
                )
            else:
                # Mini-Boss stats
                boss_stats = {
                    "hp": int((min_level * 40 + 100) * 2.5),
                    "atk": int((min_level * 8 + 15) * 1.8),
                    "def": int((min_level * 4 + 8) * 1.5),
                    "exp_reward": min_level * 250 + 100
                }
                boss = Enemy(
                    enemy_id=f"boss_{self.current_map_id}",
                    name=boss_name,
                    sprite_type="yuan_boss",
                    grid_x=x,
                    grid_y=y,
                    stats=boss_stats,
                    is_boss=True
                )
                
            self.enemies.append(boss)

    def handle_transition(self, target_x: int, target_y: int) -> None:
        """Checks and triggers scene transitions when player tries to walk off-screen."""
        map_data = MAPS[self.current_map_id]
        connections = map_data.get("connections", {})
        
        # Check transition based on direction
        transition_info = None
        if target_y < 0:
            transition_info = connections.get("north")
        elif target_y >= MAP_HEIGHT:
            transition_info = connections.get("south")
        elif target_x < 0:
            transition_info = connections.get("west")
        elif target_x >= MAP_WIDTH:
            transition_info = connections.get("east")
            
        if transition_info:
            new_map_id = transition_info["map_id"]
            start_x = transition_info["start_x"]
            start_y = transition_info["start_y"]
            
            # Check level restriction for target map
            target_map = MAPS.get(new_map_id)
            if target_map:
                min_level = target_map.get("min_level", 1)
                if self.player.level < min_level:
                    # Player level is too low! Block transition and show warning dialogue.
                    play_beep(150, 300, 0.15) # Play low warning buzz
                    self.start_dialogue("系统", [f"进入失败！【{target_map['name']}】非常危险，等级需达到 {min_level} 级以上。"])
                    return
            
            self.fade_transition(new_map_id, start_x, start_y)

    def fade_transition(self, new_map_id: str, start_x: int, start_y: int) -> None:
        """Performs a beautiful retro fade-out and fade-in screen transition."""
        # Capture current screen
        temp_surf = screen.copy()
        
        # Fade out to black
        for alpha in range(0, 256, 16):
            screen.blit(temp_surf, (0, 0))
            fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_overlay.fill(COLOR_BLACK)
            fade_overlay.set_alpha(alpha)
            screen.blit(fade_overlay, (0, 0))
            pygame.display.flip()
            clock.tick(60)
            
        # Switch map data
        self.current_map_id = new_map_id
        self.spawn_enemies_for_current_map()
        self.player.grid_x = start_x
        self.player.grid_y = start_y
        self.player.target_grid_x = start_x
        self.player.target_grid_y = start_y
        self.player.pixel_x = start_x * TILE_SIZE
        self.player.pixel_y = start_y * TILE_SIZE
        self.player.is_moving = False
        self.player.anim_frame = 0
        
        # Play transition sound
        play_beep(300, 100, 0.1)
        pygame.time.wait(50)
        play_beep(450, 150, 0.1)
        
        # Render the new scene onto the temporary surface
        self.render_scene_to_surf(temp_surf)
        
        # Fade in from black
        for alpha in range(255, -1, -16):
            screen.blit(temp_surf, (0, 0))
            fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_overlay.fill(COLOR_BLACK)
            fade_overlay.set_alpha(alpha)
            screen.blit(fade_overlay, (0, 0))
            pygame.display.flip()
            clock.tick(60)
            
        # Trigger story if first time entering this scene
        self.trigger_story(new_map_id)

    def trigger_interaction(self) -> None:
        """Checks the tile in front of the player and triggers interaction (NPC dialogue or Chest)."""
        dx, dy = 0, 0
        if self.player.direction == DIR_DOWN:
            dy = 1
        elif self.player.direction == DIR_UP:
            dy = -1
        elif self.player.direction == DIR_LEFT:
            dx = -1
        elif self.player.direction == DIR_RIGHT:
            dx = 1
            
        front_x = self.player.grid_x + dx
        front_y = self.player.grid_y + dy
        
        map_data = MAPS[self.current_map_id]
        obstacle_map = map_data["obstacle"]
        npcs = map_data["npcs"]
        chests = map_data["chests"]
        
        # 1. Check NPCs
        for npc in npcs:
            if npc["x"] == front_x and npc["y"] == front_y:
                self.start_dialogue(npc["name"], npc["dialogue"])
                play_chime_talk()
                return
                
        # 2. Check Chests
        for chest in chests:
            if chest["x"] == front_x and chest["y"] == front_y:
                if not chest["opened"]:
                    chest["opened"] = True
                    # Add item to player inventory
                    item_name = chest["item"]
                    if item_name not in self.player.inventory:
                        self.player.inventory.append(item_name)
                    
                    # Auto-equip if it's a weapon or armor item
                    if item_name in ["破旧的木棍", "精致的木棍", "精致的铁剑"]:
                        self.player.weapon = item_name
                    elif item_name in ["精致的草鞋"]:
                        self.player.equipment["靴子"] = item_name
                    
                    # Award some gold and exp
                    self.player.gold += 50
                    leveled_up = self.player.gain_exp(120)
                    
                    msg = [
                        chest["dialogue"],
                        "获得 50 文钱和 120 点经验！"
                    ]
                    if leveled_up:
                        msg.append(f"🎉 恭喜！你的等级提升到了 {self.player.level} 级！")
                        
                    self.start_dialogue("系统", msg)
                    play_chime_success()
                else:
                    self.start_dialogue("系统", ["宝箱已经是空的了。"])
                    play_beep(400, 100, 0.1)
                return

        # 3. Check Signpost and other interactive elements
        if 0 <= front_x < MAP_WIDTH and 0 <= front_y < MAP_HEIGHT:
            obs_char = obstacle_map[front_y][front_x]
            if obs_char == 'S':
                if self.current_map_id == "north":
                    self.start_dialogue("路标", [
                        "← 往左：濠州府城 (未解锁)",
                        "→ 往右：皇觉寺 (朱元璋修行之地)",
                        "↓ 往下：钟离县-南 (朱家村麦田)"
                    ])
                elif self.current_map_id == "south":
                    self.start_dialogue("路标", [
                        "↑ 往上：钟离县-北 (朱家村广场)",
                        "↓ 往下：江南古道 (未解锁)",
                        "→ 往右：常家庄 (常遇春故里)"
                    ])
                else:
                    self.start_dialogue("路标", [
                        "这里是通往大明江山的古道，继续前进吧！"
                    ])
                play_chime_talk()
                return
            elif obs_char == 'J':
                self.start_dialogue("水井", ["一口清澈的古井。井水倒映着你坚毅的面庞，手里还紧紧攥着要饭的破碗。"])
                play_chime_talk()
                return
            elif obs_char == 'Y':
                self.start_dialogue("石碑", ["‘钟离县朱家村’ —— 乱世之中，唯有自强不息，方能拯救苍生。"])
                play_chime_talk()
                return

    def start_dialogue(self, speaker: str, lines: list[str]) -> None:
        self.state = STATE_DIALOGUE
        self.dialogue_speaker = speaker
        self.dialogue_lines = lines
        self.dialogue_index = 0
        self.dialogue_text = ""
        self.dialogue_char_index = 0
        self.dialogue_timer = 0

    def update_dialogue(self) -> None:
        current_line = self.dialogue_lines[self.dialogue_index]
        if self.dialogue_char_index < len(current_line):
            self.dialogue_timer += 1
            if self.dialogue_timer >= self.dialogue_speed:
                self.dialogue_timer = 0
                self.dialogue_char_index += 1
                self.dialogue_text = current_line[:self.dialogue_char_index]
                if self.dialogue_char_index % 2 == 0:
                    play_beep(300, 20, 0.05)

    def advance_dialogue(self) -> None:
        current_line = self.dialogue_lines[self.dialogue_index]
        if self.dialogue_char_index < len(current_line):
            self.dialogue_char_index = len(current_line)
            self.dialogue_text = current_line
            play_beep(400, 30, 0.08)
        else:
            self.dialogue_index += 1
            if self.dialogue_index < len(self.dialogue_lines):
                self.dialogue_text = ""
                self.dialogue_char_index = 0
                play_beep(500, 40, 0.08)
            else:
                self.state = STATE_NORMAL
                play_beep(400, 50, 0.08)
                
                # Check for one-time NPC interaction reward
                if self.dialogue_speaker not in ["系统", "路标", "水井", "石碑"]:
                    talked_key = f"{self.current_map_id}_{self.dialogue_speaker}"
                    if talked_key not in self.talked_npcs:
                        self.talked_npcs.add(talked_key)
                        self.player.gold += 20
                        leveled_up = self.player.gain_exp(50)
                        
                        msg = [
                            f"首次与【{self.dialogue_speaker}】交谈获得 20 文钱和 50 点经验！"
                        ]
                        if leveled_up:
                            msg.append(f"🎉 恭喜！你的等级提升到了 {self.player.level} 级！")
                            
                        self.start_dialogue("系统", msg)
                        play_chime_success()

    def render_scene_to_surf(self, surface: pygame.Surface) -> None:
        """Renders the entire game scene onto a surface (used for normal loop and transitions)."""
        surface.fill(COLOR_BLACK)
        
        # Calculate Camera Offset (centered on player, clamped to map)
        camera_x = self.player.pixel_x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        camera_y = self.player.pixel_y - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        
        camera_x = max(0, min(camera_x, MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))

        # Get current map data
        map_data = MAPS[self.current_map_id]
        ground_map = map_data["ground"]
        obstacle_map = map_data["obstacle"]
        npcs = map_data["npcs"]
        chests = map_data["chests"]
        
        # Frustum Culling
        start_col = max(0, camera_x // TILE_SIZE)
        end_col = min(MAP_WIDTH, (camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        start_row = max(0, camera_y // TILE_SIZE)
        end_row = min(MAP_HEIGHT, (camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)
        
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                screen_x = col * TILE_SIZE - camera_x
                screen_y = row * TILE_SIZE - camera_y
                
                # Draw Ground
                ground_char = ground_map[row][col]
                if ground_char in self.assets.tiles:
                    surface.blit(self.assets.tiles[ground_char], (screen_x, screen_y))
                    
                # Bridge overlay
                if ground_char == 'b':
                    pygame.draw.rect(surface, (109, 76, 65), (screen_x, screen_y + 8, TILE_SIZE, TILE_SIZE - 16))
                    for px in range(screen_x, screen_x + TILE_SIZE, 8):
                        pygame.draw.line(surface, (78, 52, 46), (px, screen_y + 8), (px, screen_y + TILE_SIZE - 8), 2)
                
                # Draw Obstacles / Objects
                obs_char = obstacle_map[row][col]
                if obs_char != '.' and obs_char in self.assets.tiles:
                    if obs_char == 'C':
                        is_opened = False
                        for chest in chests:
                            if chest["x"] == col and chest["y"] == row:
                                is_opened = chest["opened"]
                                break
                        if is_opened:
                            surface.blit(self.assets.tiles[obs_char], (screen_x, screen_y))
                            pygame.draw.rect(surface, (100, 100, 100), (screen_x + 8, screen_y + 12, TILE_SIZE - 16, TILE_SIZE - 20))
                        else:
                            surface.blit(self.assets.tiles[obs_char], (screen_x, screen_y))
                    else:
                        surface.blit(self.assets.tiles[obs_char], (screen_x, screen_y))

        # Draw NPCs
        for npc in npcs:
            if start_col <= npc["x"] < end_col and start_row <= npc["y"] < end_row:
                npc_screen_x = npc["x"] * TILE_SIZE - camera_x
                npc_screen_y = npc["y"] * TILE_SIZE - camera_y
                
                # Draw the correct NPC sprite, fall back to player down_0 if missing
                sprite_id = npc["sprite"]
                if sprite_id in self.assets.npc_sprites:
                    sprite = self.assets.npc_sprites[sprite_id]
                else:
                    sprite = self.assets.player_sprites[DIR_DOWN][0]
                    
                surface.blit(sprite, (npc_screen_x, npc_screen_y))
                
                # Speech bubble indicator
                dist_x = abs(self.player.grid_x - npc["x"])
                dist_y = abs(self.player.grid_y - npc["y"])
                if (dist_x == 1 and dist_y == 0) or (dist_x == 0 and dist_y == 1):
                    pygame.draw.circle(surface, COLOR_GOLD, (npc_screen_x + TILE_SIZE // 2, npc_screen_y - 8), 8)
                    pygame.draw.circle(surface, COLOR_BLACK, (npc_screen_x + TILE_SIZE // 2, npc_screen_y - 8), 8, 1)
                    pygame.draw.circle(surface, COLOR_WHITE, (npc_screen_x + TILE_SIZE // 2, npc_screen_y - 8), 2)

        # Draw Enemies (Delegated to enemy_renderer.py)
        draw_enemies(surface, self.enemies, camera_x, camera_y, start_col, end_col, start_row, end_row,
                     self.assets.enemy_sprites, self.font_small, TILE_SIZE, COLOR_GOLD, COLOR_RED)

        # Draw Player
        self.player.draw(surface, camera_x, camera_y, self.assets.player_sprites)

    def run(self) -> None:
        # Trigger story for the starting scene
        self.trigger_story(self.current_map_id)
        
        running = True
        while running:
            # 1. Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == STATE_NORMAL:
                        if event.key == pygame.K_SPACE:
                            self.trigger_interaction()
                        elif event.key == pygame.K_g:
                            # Toggle AFK/Idle experience
                            self.player.is_afk_enabled = not self.player.is_afk_enabled
                            if self.player.is_afk_enabled:
                                play_chime_success()
                            else:
                                play_beep(150, 150, 0.1)
                    elif self.state == STATE_DIALOGUE:
                        if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                            self.advance_dialogue()
                    elif self.state == STATE_STORY:
                        if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                            self.advance_story()
                    elif self.state == STATE_EQUIP_CHOICE:
                        if event.key == pygame.K_1 or event.key == pygame.K_y:
                            # REPLACE
                            self.confirm_equip_replace()
                        elif event.key == pygame.K_2 or event.key == pygame.K_n or event.key in [pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_d]:
                            # DISCARD
                            self.discard_equip_drop()

            # 2. Handle Continuous Key Presses (for movement)
            if self.state == STATE_NORMAL and not self.player.is_moving:
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0
                direction = None
                
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    dy = -1
                    direction = DIR_UP
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    dy = 1
                    direction = DIR_DOWN
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    dx = -1
                    direction = DIR_LEFT
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    dx = 1
                    direction = DIR_RIGHT
                    
                if direction:
                    self.player.move(dx, dy, direction, self.is_tile_solid, self.handle_transition)

            # 3. Update Game Objects
            afk_leveled_up = self.player.update()
            if afk_leveled_up:
                play_chime_success()
                if self.state == STATE_NORMAL:
                    self.start_dialogue("系统", [f"🎉 挂机修行有成！你的等级提升到了 {self.player.level} 级！"])
            
            if self.state == STATE_NORMAL:
                for enemy in self.enemies:
                    enemy.update(self.player.grid_x, self.player.grid_y, self.is_tile_solid_for_enemy)
            
            if self.state == STATE_DIALOGUE:
                self.update_dialogue()
            elif self.state == STATE_STORY:
                self.update_story()

            # Update Battle Cooldown Timer
            if self.battle_cooldown_timer > 0:
                self.battle_cooldown_timer -= 1

            # Update Chopping Progress
            if self.state == STATE_NORMAL:
                # Check for battle trigger first
                near_monster = self.get_near_monster()
                near_enemy = self.get_near_enemy()
                if (near_monster or near_enemy) and self.battle_cooldown_timer <= 0:
                    self.state = STATE_BATTLE
                    self.battle_start_time = pygame.time.get_ticks()
                    if near_enemy:
                        self.battle_enemy = near_enemy
                        self.battle_monster_id = None
                        self.battle_monster_sprite = None
                    else:
                        self.battle_enemy = None
                        self.battle_monster_id = near_monster["id"]
                        self.battle_monster_sprite = near_monster["sprite"]
                    play_beep(200, 300, 0.3)
                    self.chopping_start_time = None
                elif self.is_near_tree():
                    if self.chopping_start_time is None:
                        self.chopping_start_time = pygame.time.get_ticks()
                    else:
                        elapsed = pygame.time.get_ticks() - self.chopping_start_time
                        if elapsed >= 5000:
                            self.roll_random_equipment_drop()
                            self.chopping_start_time = None
                else:
                    self.chopping_start_time = None
            else:
                self.chopping_start_time = None

            # Update Battle Progress
            if self.state == STATE_BATTLE:
                if self.battle_start_time is not None:
                    elapsed = pygame.time.get_ticks() - self.battle_start_time
                    if elapsed >= 5000:
                        # Simulate battle
                        if self.battle_enemy:
                            win, battle_log = self.simulate_battle(None, self.battle_enemy)
                            m_name = self.battle_enemy.name
                            exp_reward = self.battle_enemy.exp_reward
                            is_ultimate = self.battle_enemy.is_ultimate_boss
                        else:
                            win, battle_log = self.simulate_battle(self.battle_monster_sprite)
                            monster = self.monster_table.get(self.battle_monster_sprite)
                            m_name = monster["name"] if monster else "野怪"
                            exp_reward = monster["exp_reward"] if monster else 100
                            is_ultimate = False
                        
                        if win:
                            # Win!
                            if self.battle_enemy:
                                if self.battle_enemy in self.enemies:
                                    self.enemies.remove(self.battle_enemy)
                            else:
                                self.remove_monster_npc(self.battle_monster_id)
                                
                            leveled_up = self.player.gain_exp(exp_reward)
                            
                            msg = [
                                f"🎉 战斗胜利！你成功击败了【{m_name}】！",
                                f"获得大量的经验奖励：+{exp_reward} 点！"
                            ]
                            if leveled_up:
                                msg.append(f"🎉 恭喜！你的等级提升到了 {self.player.level} 级！")
                                
                            if is_ultimate:
                                msg.append("🏆 恭喜你！你成功击败了元朝皇帝妥欢贴睦尔，攻克了元大都！")
                                msg.append("🏆 历经千难万险，你终于推翻了暴元统治，驱逐鞑虏，恢复中华！")
                                msg.append("🏆 你在南京称帝，国号【大明】，年号【洪武】！")
                                msg.append("🏆 属于你的大明盛世，自此开启！感谢游玩！")
                                
                            self.state = STATE_DIALOGUE
                            self.start_dialogue("战斗结果", msg)
                            play_chime_success()
                        else:
                            # Lose!
                            # Calculate HP deduction based on the combat power of the enemy/monster
                            if self.battle_enemy:
                                # For enemies, combat power can be represented by their ATK and Max HP
                                hp_loss = int(self.battle_enemy.atk * 0.5 + self.battle_enemy.max_hp * 0.1)
                            else:
                                # For wild animals / monsters
                                monster = self.monster_table.get(self.battle_monster_sprite)
                                if monster:
                                    hp_loss = int(monster["atk"] * 0.5 + monster["hp"] * 0.1)
                                else:
                                    hp_loss = 20  # Fallback
                            
                            # Deduct HP, ensuring it doesn't go below 1 (or if it goes below 1, we can reset to 1 to avoid game over, or handle death)
                            # Let's deduct HP but clamp it to a minimum of 1 HP so the player doesn't instantly die, or we can let them die and respawn!
                            # Let's make a nice design: if player HP drops to 0, they get sent back to the starting map (north) with full HP as a penalty, or we just clamp to 1 HP.
                            # Clamping to 1 HP is friendly, but respawning at starting map is a classic RPG mechanic! Let's do a classic RPG penalty:
                            # If HP <= 0, they "faint" and respawn at "濠州府 · 钟离县-北" with full HP, losing some gold/experience.
                            # Let's check user's request: "如果攻击动物或敌人失败，会扣除部分血量，扣除多少以动物或敌人的战斗力决定"
                            # Let's deduct the blood!
                            self.player.hp -= hp_loss
                            fainted = False
                            if self.player.hp <= 0:
                                self.player.hp = self.player.max_hp
                                fainted = True
                                
                            msg = [
                                f"💀 战斗失败！你被【{m_name}】击败了！",
                                f"你受到了重创，生命值扣除了 {hp_loss} 点！"
                            ]
                            
                            if fainted:
                                msg.append("💀 你伤势过重昏迷了过去……")
                                msg.append("🏥 幸好被路过的行脚医生救起，送回了【濠州府 · 钟离县-北】。")
                                msg.append("🏥 你的生命值已恢复满，但请务必小心，先提升实力再战！")
                            else:
                                msg.append(f"❤️ 剩余生命值: {self.player.hp}/{self.player.max_hp}")
                                msg.append("系统提示：你现在的攻击力和防御力还不太行，建议提升等级或更换更强力的装备后再来挑战！")
                                
                            self.state = STATE_DIALOGUE
                            self.start_dialogue("战斗结果", msg)
                            play_beep(150, 400, 0.5)
                            
                            if fainted:
                                # Respawn at north map
                                self.fade_transition("north", 13, 5)
                            else:
                                # Push player back 1 tile to prevent immediate re-trigger
                                opp_dx, opp_dy = 0, 0
                                if self.player.direction == DIR_UP: opp_dy = 1
                                elif self.player.direction == DIR_DOWN: opp_dy = -1
                                elif self.player.direction == DIR_LEFT: opp_dx = 1
                                elif self.player.direction == DIR_RIGHT: opp_dx = -1
                                
                                new_x = self.player.grid_x + opp_dx
                                new_y = self.player.grid_y + opp_dy
                                if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT and not self.is_tile_solid(new_x, new_y):
                                    self.player.grid_x = self.player.target_grid_x = new_x
                                    self.player.grid_y = self.player.target_grid_y = new_y
                                    self.player.pixel_x = new_x * TILE_SIZE
                                    self.player.pixel_y = new_y * TILE_SIZE
                                
                        self.battle_start_time = None
                        self.battle_monster_id = None
                        self.battle_enemy = None
                        self.battle_cooldown_timer = 180 # 3 seconds cooldown
            else:
                self.battle_start_time = None
                self.battle_monster_id = None
                self.battle_enemy = None

            # Update Equip Choice Timeout
            if self.state == STATE_EQUIP_CHOICE:
                elapsed_choice = pygame.time.get_ticks() - self.choice_start_time
                if elapsed_choice >= 3000:
                    self.compare_and_decide_equip()

            # 4. Render normal scene onto screen
            self.render_scene_to_surf(screen)

            # 5. Draw HUD / UI
            
            # --- Top-Right: Scene Name ---
            scene_name = MAPS[self.current_map_id]["name"]
            text_surf = self.font_title.render(scene_name, True, COLOR_GOLD)
            padding = 12
            box_width = text_surf.get_width() + padding * 2
            box_height = text_surf.get_height() + padding * 2
            box_rect = pygame.Rect(SCREEN_WIDTH - box_width - 16, 16, box_width, box_height)
            
            pygame.draw.rect(screen, COLOR_UI_BG, box_rect)
            pygame.draw.rect(screen, COLOR_UI_BORDER, box_rect, 3)
            pygame.draw.rect(screen, COLOR_BLACK, box_rect.inflate(-6, -6), 1)
            
            screen.blit(text_surf, (box_rect.x + padding, box_rect.y + padding))

            # --- Top-Left: Player RPG Status Panel ---
            panel_w = 320
            panel_h = 245
            px, py = 16, 16
            
            # Create a semi-transparent Surface
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            
            # Draw solid semi-transparent rounded rectangle (Dark charcoal blue-black, alpha=210)
            pygame.draw.rect(panel_surf, (15, 23, 42, 210), (0, 0, panel_w, panel_h), border_radius=12)
            
            # Draw beautiful metallic golden-orange border
            pygame.draw.rect(panel_surf, (255, 193, 7, 230), (0, 0, panel_w, panel_h), width=3, border_radius=12)
            # Inner thin white highlight border for glowing/glass effect
            pygame.draw.rect(panel_surf, (255, 255, 255, 30), (4, 4, panel_w - 8, panel_h - 8), width=1, border_radius=8)
            
            # Render attributes
            # 1. Player Name
            name_surf = self.font_title.render(f"👑 {self.player.name}", True, COLOR_GOLD)
            panel_surf.blit(name_surf, (20, 14))
            
            # 2. Level tag (pill shaped badge)
            lvl_surf = self.font_ui.render(f"Lv. {self.player.level}", True, (0, 229, 255)) # bright cyan
            panel_surf.blit(lvl_surf, (panel_w - 85, 18))
            
            # Draw decorative horizontal divider line
            pygame.draw.line(panel_surf, (255, 255, 255, 45), (20, 48), (panel_w - 20, 48), 2)
            
            # 3. EXP Bar (with text centered inside)
            max_exp = self.player.level * 100
            current_exp = self.player.exp
            exp_pct = max(0.0, min(1.0, current_exp / max_exp))
            
            bar_x, bar_y = 20, 56
            bar_w = panel_w - 40
            bar_h = 16
            pygame.draw.rect(panel_surf, (30, 41, 59, 255), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            if exp_pct > 0:
                pygame.draw.rect(panel_surf, (16, 185, 129, 255), (bar_x, bar_y, int(bar_w * exp_pct), bar_h), border_radius=4)
            
            exp_text = f"经验: {current_exp}/{max_exp} ({int(exp_pct*100)}%)"
            exp_label_surf = self.font_small.render(exp_text, True, (255, 255, 255))
            tx = bar_x + (bar_w - exp_label_surf.get_width()) // 2
            ty = bar_y + (bar_h - exp_label_surf.get_height()) // 2
            panel_surf.blit(exp_label_surf, (tx, ty))
            
            # 3.5 HP Bar (with text centered inside)
            max_hp = self.player.max_hp
            current_hp = self.player.hp
            hp_pct = max(0.0, min(1.0, current_hp / max_hp))
            
            hp_bar_x, hp_bar_y = 20, 78
            hp_bar_w = panel_w - 40
            hp_bar_h = 16
            pygame.draw.rect(panel_surf, (30, 41, 59, 255), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=4)
            if hp_pct > 0:
                pygame.draw.rect(panel_surf, (239, 68, 68, 255), (hp_bar_x, hp_bar_y, int(hp_bar_w * hp_pct), hp_bar_h), border_radius=4)
            
            hp_text = f"生命值: {current_hp}/{max_hp} ({int(hp_pct*100)}%)"
            hp_label_surf = self.font_small.render(hp_text, True, (255, 255, 255))
            tx = hp_bar_x + (hp_bar_w - hp_label_surf.get_width()) // 2
            ty = hp_bar_y + (hp_bar_h - hp_label_surf.get_height()) // 2
            panel_surf.blit(hp_label_surf, (tx, ty))

            # 4. RPG stats: Attack, Defense, Weapon, Gold
            stat_y = 104
            line_h = 24
            
            # Stats: Attack and Defense in a row
            atk_surf = self.font_ui.render(f"⚔️ 攻击力: {self.player.attack}", True, (248, 113, 113)) # soft coral red
            def_surf = self.font_ui.render(f"🛡️ 防御力: {self.player.defense}", True, (96, 165, 250))  # soft blue
            panel_surf.blit(atk_surf, (20, stat_y))
            panel_surf.blit(def_surf, (170, stat_y))
            
            # Stat: Current Weapon
            wpn_surf = self.font_ui.render(f"🗡️ 武器: {self.player.weapon}", True, (253, 186, 116)) # light orange
            panel_surf.blit(wpn_surf, (20, stat_y + line_h))
            
            # Stat: Gold
            gold_surf = self.font_ui.render(f"💰 银两: {self.player.gold} 文", True, (253, 224, 71)) # soft yellow
            panel_surf.blit(gold_surf, (20, stat_y + line_h * 2))
            
            # Divider before status
            pygame.draw.line(panel_surf, (255, 255, 255, 25), (20, stat_y + line_h * 3 + 2), (panel_w - 20, stat_y + line_h * 3 + 2), 1)
            
            # Stat: AFK Idle status
            if self.player.is_afk_enabled:
                idle_surf = self.font_ui.render("🍃 挂机修炼中 (+5 经验/秒)", True, (52, 211, 153)) # bright mint green
            else:
                idle_surf = self.font_ui.render("💤 挂机修炼已暂停", True, (148, 163, 184)) # muted grey
            panel_surf.blit(idle_surf, (20, stat_y + line_h * 3 + 6))
            
            # Pulsing breathing dot animation
            if self.player.is_afk_enabled:
                pulse_alpha = int(127 + 128 * math.sin(pygame.time.get_ticks() / 150))
                pulse_color = (52, 211, 153, max(0, min(255, pulse_alpha)))
            else:
                pulse_color = (148, 163, 184, 150) # solid dim grey when paused
                
            pulse_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surf, pulse_color, (6, 6), 5)
            panel_surf.blit(pulse_surf, (panel_w - 28, stat_y + line_h * 3 + 10))
            
            # Blit the entire panel onto screen
            screen.blit(panel_surf, (px, py))

            # --- Top-Left: Player RPG Equipment Panel ---
            eq_panel_w = 320
            eq_panel_h = 155
            eq_px, eq_py = 16, 16 + panel_h + 8  # Start at 269, fits perfectly above 440 dialogue box
            
            # Create a semi-transparent Surface for equipment
            eq_panel_surf = pygame.Surface((eq_panel_w, eq_panel_h), pygame.SRCALPHA)
            
            # Draw solid semi-transparent rounded rectangle (alpha=190 for glassmorphism overlay feel)
            pygame.draw.rect(eq_panel_surf, (15, 23, 42, 195), (0, 0, eq_panel_w, eq_panel_h), border_radius=12)
            
            # Draw beautiful golden border (matching status panel, width=2)
            pygame.draw.rect(eq_panel_surf, (255, 193, 7, 210), (0, 0, eq_panel_w, eq_panel_h), width=2, border_radius=12)
            # Inner thin white highlight
            pygame.draw.rect(eq_panel_surf, (255, 255, 255, 20), (3, 3, eq_panel_w - 6, eq_panel_h - 6), width=1, border_radius=9)
            
            # Subtitles: Attack items (Left) and Defense items (Right)
            eq_panel_surf.blit(self.font_small.render("⚔️ 攻具 (Offensive)", True, (252, 165, 165)), (14, 8))
            eq_panel_surf.blit(self.font_small.render("🛡️ 防具 (Defensive)", True, (147, 197, 253)), (170, 8))
            
            # Divider under subtitles
            pygame.draw.line(eq_panel_surf, (255, 255, 255, 30), (14, 25), (eq_panel_w - 14, 25), 1)
            
            # Grids layout parameters
            grid_w = 138
            grid_h = 21
            col_gap = 16
            row_gap = 3
            start_x = 14
            start_y = 30
            
            # Define Offensive and Defensive items in lists for easy looping
            off_parts = ["武器", "护腕", "项链", "护符", "戒指"]
            def_parts = ["帽子", "护手", "护肩", "腰带", "靴子"]
            
            for i in range(5):
                # --- Left column: Offensive Grid ---
                part_off = off_parts[i]
                item_off = self.player.equipment.get(part_off)
                
                bx_off = start_x
                by_off = start_y + i * (grid_h + row_gap)
                box_rect_off = pygame.Rect(bx_off, by_off, grid_w, grid_h)
                
                if item_off:
                    # Equipped: Draw glowing emerald green/teal background
                    pygame.draw.rect(eq_panel_surf, (16, 185, 129, 35), box_rect_off, border_radius=4)
                    pygame.draw.rect(eq_panel_surf, (16, 185, 129, 150), box_rect_off, width=1, border_radius=4)
                    
                    text_str = f"🗡️ {item_off}"
                    txt_surf = self.font_ui.render(text_str, True, (253, 224, 71)) # Gold
                    if txt_surf.get_width() > grid_w - 6:
                        txt_surf = self.font_small.render(text_str, True, (253, 224, 71))
                else:
                    # Empty: Draw slate-grey thin box
                    pygame.draw.rect(eq_panel_surf, (30, 41, 59, 100), box_rect_off, border_radius=4)
                    pygame.draw.rect(eq_panel_surf, (71, 85, 105, 100), box_rect_off, width=1, border_radius=4)
                    
                    text_str = part_off
                    txt_surf = self.font_ui.render(text_str, True, (148, 163, 184)) # Muted grey
                    
                # Center text inside grid box
                tx_x = bx_off + (grid_w - txt_surf.get_width()) // 2
                tx_y = by_off + (grid_h - txt_surf.get_height()) // 2
                eq_panel_surf.blit(txt_surf, (tx_x, tx_y))
                
                # --- Right column: Defensive Grid ---
                part_def = def_parts[i]
                item_def = self.player.equipment.get(part_def)
                
                bx_def = start_x + grid_w + col_gap
                by_def = start_y + i * (grid_h + row_gap)
                box_rect_def = pygame.Rect(bx_def, by_def, grid_w, grid_h)
                
                if item_def:
                    # Equipped: Draw magical sky-blue background
                    pygame.draw.rect(eq_panel_surf, (59, 130, 246, 35), box_rect_def, border_radius=4)
                    pygame.draw.rect(eq_panel_surf, (59, 130, 246, 150), box_rect_def, width=1, border_radius=4)
                    
                    text_str = f"🛡️ {item_def}"
                    txt_surf = self.font_ui.render(text_str, True, (147, 197, 253)) # Soft blue
                    if txt_surf.get_width() > grid_w - 6:
                        txt_surf = self.font_small.render(text_str, True, (147, 197, 253))
                else:
                    # Empty: Draw slate-grey thin box
                    pygame.draw.rect(eq_panel_surf, (30, 41, 59, 100), box_rect_def, border_radius=4)
                    pygame.draw.rect(eq_panel_surf, (71, 85, 105, 100), box_rect_def, width=1, border_radius=4)
                    
                    text_str = part_def
                    txt_surf = self.font_ui.render(text_str, True, (148, 163, 184)) # Muted grey
                    
                # Center text inside grid box
                tx_x = bx_def + (grid_w - txt_surf.get_width()) // 2
                tx_y = by_def + (grid_h - txt_surf.get_height()) // 2
                eq_panel_surf.blit(txt_surf, (tx_x, tx_y))
            
            # Blit the entire equipment panel onto screen
            screen.blit(eq_panel_surf, (eq_px, eq_py))

            # --- Pop-up: Equip Drop Choice Screen ---
            if self.state == STATE_EQUIP_CHOICE and self.dropped_equip and self.dropped_slot:
                choice_w = 460
                choice_h = 280
                cx = (SCREEN_WIDTH - choice_w) // 2
                cy = (SCREEN_HEIGHT - choice_h) // 2
                
                # Semi-transparent choice background
                choice_surf = pygame.Surface((choice_w, choice_h), pygame.SRCALPHA)
                pygame.draw.rect(choice_surf, (15, 23, 42, 235), (0, 0, choice_w, choice_h), border_radius=16)
                
                # Quality Colors
                # Quality map: 白->white, 绿->green, 蓝->cyan, 紫->purple, 橙->orange/gold
                q_colors = {
                    "白": (241, 245, 249),
                    "绿": (34, 197, 94),
                    "蓝": (59, 130, 246),
                    "紫": (168, 85, 247),
                    "橙": (245, 158, 11)
                }
                drop_quality = self.dropped_equip.get("quality", "白")
                q_color = q_colors.get(drop_quality, COLOR_WHITE)
                
                # Draw thick quality-colored glowing border
                pygame.draw.rect(choice_surf, q_color, (0, 0, choice_w, choice_h), width=4, border_radius=16)
                pygame.draw.rect(choice_surf, (255, 255, 255, 30), (5, 5, choice_w - 10, choice_h - 10), width=1, border_radius=12)
                
                # Title
                title_text = f"✨ 发现了神兵遗宝 ({self.dropped_slot}) ✨"
                title_surf = self.font_title.render(title_text, True, COLOR_GOLD)
                choice_surf.blit(title_surf, ((choice_w - title_surf.get_width()) // 2, 16))
                
                # Decorative Divider
                pygame.draw.line(choice_surf, (255, 255, 255, 35), (20, 52), (choice_w - 20, 52), 2)
                
                # Columns: Left (Current Equip), Right (Dropped Equip)
                col_w = 200
                col_h = 135
                
                # --- Left Column: Current ---
                curr_item_name = self.player.equipment.get(self.dropped_slot)
                
                # Find current item stats
                curr_item_stats = "无"
                curr_item_quality = "白"
                if curr_item_name:
                    # Let's locate quality and stats of current item from table
                    found = False
                    for slot, items in self.equipment_table.items():
                        for it in items:
                            if it["name"] == curr_item_name:
                                curr_item_quality = it["get"] if "get" in it else it.get("quality", "白")
                                if it.get("atk", 0) > 0:
                                    curr_item_stats = f"攻击 +{it['atk']}"
                                elif it.get("def", 0) > 0:
                                    curr_item_stats = f"防御 +{it['def']}"
                                found = True
                                break
                        if found: break
                else:
                    curr_item_name = "（空空如也）"
                    
                curr_q_color = q_colors.get(curr_item_quality, (148, 163, 184))
                
                # Draw Left Card Box
                pygame.draw.rect(choice_surf, (30, 41, 59, 120), (20, 68, col_w, col_h), border_radius=8)
                pygame.draw.rect(choice_surf, (71, 85, 105, 80), (20, 68, col_w, col_h), width=1, border_radius=8)
                
                lbl_curr_head = self.font_small.render("当前穿戴部位", True, (148, 163, 184))
                choice_surf.blit(lbl_curr_head, (30, 76))
                
                lbl_curr_name = self.font_ui.render(curr_item_name, True, curr_q_color)
                # scale font down if too wide
                if lbl_curr_name.get_width() > col_w - 20:
                    lbl_curr_name = self.font_small.render(curr_item_name, True, curr_q_color)
                choice_surf.blit(lbl_curr_name, (30, 102))
                
                lbl_curr_q = self.font_small.render(f"品质: {curr_item_quality}级", True, curr_q_color)
                choice_surf.blit(lbl_curr_q, (30, 134))
                lbl_curr_st = self.font_ui.render(f"属性: {curr_item_stats}", True, COLOR_WHITE)
                choice_surf.blit(lbl_curr_st, (30, 158))
                
                # --- VS MIDDLE ARROW ---
                vs_text = "VS"
                vs_surf = self.font_title.render(vs_text, True, (156, 163, 175))
                choice_surf.blit(vs_surf, (226, 115))
                
                # --- Right Column: Dropped ---
                drop_item_name = self.dropped_equip["name"]
                drop_item_stats = "无"
                if self.dropped_equip.get("atk", 0) > 0:
                    drop_item_stats = f"攻击 +{self.dropped_equip['atk']}"
                elif self.dropped_equip.get("def", 0) > 0:
                    drop_item_stats = f"防御 +{self.dropped_equip['def']}"
                    
                # Draw Right Card Box
                pygame.draw.rect(choice_surf, (30, 41, 59, 180), (240, 68, col_w, col_h), border_radius=8)
                pygame.draw.rect(choice_surf, q_color, (240, 68, col_w, col_h), width=2, border_radius=8)
                
                lbl_drop_head = self.font_small.render("神兵掉落部位", True, (251, 191, 36))
                choice_surf.blit(lbl_drop_head, (250, 76))
                
                lbl_drop_name = self.font_ui.render(drop_item_name, True, q_color)
                if lbl_drop_name.get_width() > col_w - 20:
                    lbl_drop_name = self.font_small.render(drop_item_name, True, q_color)
                choice_surf.blit(lbl_drop_name, (250, 102))
                
                lbl_drop_q = self.font_small.render(f"品质: {drop_quality}级", True, q_color)
                choice_surf.blit(lbl_drop_q, (250, 134))
                lbl_drop_st = self.font_ui.render(f"属性: {drop_item_stats}", True, (52, 211, 153))
                choice_surf.blit(lbl_drop_st, (250, 158))
                
                # Bottom prompt options
                pygame.draw.line(choice_surf, (255, 255, 255, 35), (20, 216), (choice_w - 20, 216), 1)
                
                # Countdown Timer
                elapsed_choice = pygame.time.get_ticks() - self.choice_start_time
                remaining_sec = max(0.0, 3.0 - elapsed_choice / 1000.0)
                timer_text = f"自动决策倒计时: {remaining_sec:.1f} 秒"
                timer_surf = self.font_small.render(timer_text, True, (239, 68, 68))
                choice_surf.blit(timer_surf, ((choice_w - timer_surf.get_width()) // 2, 192))
                
                prompt_txt = "按 [1] 或 [Y] 替换穿戴  |  按 [2] 或 [N] 潇洒丢弃"
                prompt_surf = self.font_ui.render(prompt_txt, True, COLOR_GOLD)
                choice_surf.blit(prompt_surf, ((choice_w - prompt_surf.get_width()) // 2, 230))
                
                # Pulse highlight background under prompt
                p_alpha = int(140 + 60 * math.sin(pygame.time.get_ticks() / 100))
                
                # Blit popup onto center of screen
                screen.blit(choice_surf, (cx, cy))

            # --- Bottom-Center: Chopping Tree Progress Bar ---
            if self.state == STATE_NORMAL and self.is_near_tree():
                if self.chopping_start_time is not None:
                    elapsed = pygame.time.get_ticks() - self.chopping_start_time
                    progress_pct = min(1.0, elapsed / 5000.0)
                    
                    # Draw Progress Bar Container
                    pb_w = 400
                    pb_h = 36
                    pb_x = (SCREEN_WIDTH - pb_w) // 2
                    pb_y = SCREEN_HEIGHT - 80
                    
                    # Background
                    pb_bg = pygame.Surface((pb_w, pb_h), pygame.SRCALPHA)
                    pygame.draw.rect(pb_bg, (15, 23, 42, 220), (0, 0, pb_w, pb_h), border_radius=8)
                    screen.blit(pb_bg, (pb_x, pb_y))
                    
                    # Border
                    pygame.draw.rect(screen, (245, 158, 11), (pb_x, pb_y, pb_w, pb_h), width=2, border_radius=8)
                    
                    # Fill
                    if progress_pct > 0:
                        fill_w = int((pb_w - 8) * progress_pct)
                        pygame.draw.rect(screen, (34, 197, 94), (pb_x + 4, pb_y + 4, fill_w, pb_h - 8), border_radius=4)
                        
                    # Text
                    pb_text = f"🪓 正在砍树中... {int(progress_pct * 100)}%"
                    pb_text_surf = self.font_ui.render(pb_text, True, (255, 255, 255))
                    screen.blit(pb_text_surf, (pb_x + (pb_w - pb_text_surf.get_width()) // 2, pb_y + (pb_h - pb_text_surf.get_height()) // 2))

            # --- Bottom-Center: Battle Progress Bar ---
            if self.state == STATE_BATTLE:
                if self.battle_start_time is not None:
                    elapsed = pygame.time.get_ticks() - self.battle_start_time
                    progress_pct = min(1.0, elapsed / 5000.0)
                    
                    # Draw Progress Bar Container
                    pb_w = 400
                    pb_h = 36
                    pb_x = (SCREEN_WIDTH - pb_w) // 2
                    pb_y = SCREEN_HEIGHT - 80
                    
                    # Background
                    pb_bg = pygame.Surface((pb_w, pb_h), pygame.SRCALPHA)
                    pygame.draw.rect(pb_bg, (30, 41, 59, 220), (0, 0, pb_w, pb_h), border_radius=8)
                    screen.blit(pb_bg, (pb_x, pb_y))
                    
                    # Border (Red for battle!)
                    pygame.draw.rect(screen, (239, 68, 68), (pb_x, pb_y, pb_w, pb_h), width=2, border_radius=8)
                    
                    # Fill (Red/Orange for battle)
                    if progress_pct > 0:
                        fill_w = int((pb_w - 8) * progress_pct)
                        pygame.draw.rect(screen, (220, 38, 38), (pb_x + 4, pb_y + 4, fill_w, pb_h - 8), border_radius=4)
                        
                    # Text
                    monster_name = "野怪"
                    if self.battle_enemy:
                        monster_name = self.battle_enemy.name
                    elif self.battle_monster_id:
                        monster_name = self.monster_table.get(self.battle_monster_sprite, {}).get("name", "野怪")
                    pb_text = f"⚔️ 正在与【{monster_name}】激烈交战中... {int(progress_pct * 100)}%"
                    pb_text_surf = self.font_ui.render(pb_text, True, (255, 255, 255))
                    screen.blit(pb_text_surf, (pb_x + (pb_w - pb_text_surf.get_width()) // 2, pb_y + (pb_h - pb_text_surf.get_height()) // 2))

            # --- Bottom: Dialogue Box ---
            if self.state == STATE_DIALOGUE:
                dialogue_box_rect = pygame.Rect(16, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 32, 144)
                pygame.draw.rect(screen, COLOR_UI_BG, dialogue_box_rect)
                pygame.draw.rect(screen, COLOR_UI_BORDER, dialogue_box_rect, 4)
                pygame.draw.rect(screen, COLOR_BLACK, dialogue_box_rect.inflate(-8, -8), 1)
                
                # Speaker Name Tag
                speaker_surf = self.font_title.render(f"【 {self.dialogue_speaker} 】", True, COLOR_GOLD)
                screen.blit(speaker_surf, (dialogue_box_rect.x + 16, dialogue_box_rect.y + 12))
                
                # Dialogue Text (wrapped)
                chars_per_line = 32
                text_y = dialogue_box_rect.y + 48
                line_spacing = 26
                
                for i in range(0, len(self.dialogue_text), chars_per_line):
                    line_chunk = self.dialogue_text[i:i + chars_per_line]
                    chunk_surf = self.font_dialogue.render(line_chunk, True, COLOR_TEXT)
                    screen.blit(chunk_surf, (dialogue_box_rect.x + 24, text_y))
                    text_y += line_spacing
                
                # Floating "▼" prompt at bottom right when text is fully typed
                current_line_len = len(self.dialogue_lines[self.dialogue_index])
                if self.dialogue_char_index >= current_line_len:
                    if (pygame.time.get_ticks() // 300) % 2 == 0:
                        prompt_surf = self.font_dialogue.render("▼", True, COLOR_GOLD)
                        screen.blit(prompt_surf, (dialogue_box_rect.right - 32, dialogue_box_rect.bottom - 32))

            # --- Full-Screen Story Overlay ---
            if self.state == STATE_STORY:
                # Draw dark overlay
                story_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                story_overlay.fill((10, 10, 15)) # almost pitch black
                screen.blit(story_overlay, (0, 0))
                
                # Draw a beautiful parchment-like or metallic border box
                box_w = 600
                box_h = 400
                box_x = (SCREEN_WIDTH - box_w) // 2
                box_y = (SCREEN_HEIGHT - box_h) // 2
                
                # Draw outer border
                pygame.draw.rect(screen, (255, 193, 7, 200), (box_x, box_y, box_w, box_h), width=3, border_radius=16)
                pygame.draw.rect(screen, (255, 255, 255, 20), (box_x + 4, box_y + 4, box_w - 8, box_h - 8), width=1, border_radius=12)
                
                # Draw Title
                scene_name = MAPS[self.current_map_id]["name"]
                title_text = f"—— 历史纪实 · {scene_name} ——"
                title_surf = self.font_title.render(title_text, True, COLOR_GOLD)
                screen.blit(title_surf, (box_x + (box_w - title_surf.get_width()) // 2, box_y + 32))
                
                # Draw Divider
                pygame.draw.line(screen, (255, 255, 255, 40), (box_x + 40, box_y + 80), (box_x + box_w - 40, box_y + 80), 2)
                
                # Draw Story Text (wrapped)
                chars_per_line = 24
                text_y = box_y + 110
                line_spacing = 30
                
                for i in range(0, len(self.story_text), chars_per_line):
                    line_chunk = self.story_text[i:i + chars_per_line]
                    chunk_surf = self.font_dialogue.render(line_chunk, True, (241, 245, 249)) # bright slate white
                    screen.blit(chunk_surf, (box_x + 40, text_y))
                    text_y += line_spacing
                
                # Floating "▼" or "按下回车键继续..." prompt at bottom right when text is fully typed
                current_story_len = len(self.story_lines[self.story_index])
                if self.story_char_index >= current_story_len:
                    prompt_text = "按下 [回车键] 继续大业..."
                    prompt_surf = self.font_small.render(prompt_text, True, COLOR_GOLD)
                    screen.blit(prompt_surf, (box_x + box_w - prompt_surf.get_width() - 40, box_y + box_h - 40))
                    
                    if (pygame.time.get_ticks() // 300) % 2 == 0:
                        arrow_surf = self.font_dialogue.render("▼", True, COLOR_GOLD)
                        screen.blit(arrow_surf, (box_x + box_w - 32, box_y + box_h - 42))

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Print launch message
    print("==================================================")
    print("  大明王朝 RPG - 开局一个碗，帮朱元璋打天下")
    print("  游戏引擎启动中...")
    print("  操作说明:")
    print("    - 移动: 使用键盘的方向键 (↑, ↓, ←, →) 或 WASD 键")
    print("    - 互动 / 对话 / 打开宝箱: 空格键 (SPACE)")
    print("    - [挂机开关] 按下 G 键 切换/暂停挂机自动升级")
    print("    - [神木降临] 走到树木附近，自动砍树5秒掉落神兵！")
    print("    - [调试秘籍] 直接升一级: L")
    print("    - [调试秘籍] 获得50点经验: K")
    print("==================================================")
    game = Game()
    game.run()
