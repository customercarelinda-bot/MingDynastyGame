# -*- coding: utf-8 -*-
"""
Ming Dynasty RPG Map Editor.
Allows visual editing of map tiles, connections, NPCs, and saving directly back to map_data.py and JSONs.
Run: python map_editor.py
"""

from __future__ import annotations

import array
import json
import math
import os
import sys
from pathlib import Path
import pygame

# Import existing map data
from map_data import MAPS, MAP_WIDTH, MAP_HEIGHT, SCENES_DIR, BASE_DIR

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
TILE_SIZE = 32  # 32x32 for editor to fit more on screen
GRID_COLS = 40
GRID_ROWS = 30
MAP_VIEW_WIDTH = GRID_COLS * TILE_SIZE  # 1280 (Wait, 40 * 32 = 1280, which is wider than 1100. Let's use 24x24 tiles or scrollable view)

# Let's use 20x20 pixels per tile in editor to comfortably fit a 40x30 map on screen!
# 40 * 20 = 800 width, 30 * 20 = 600 height.
# This leaves 300px on the right for tools, and 100px at the bottom for status.
TILE_SIZE = 20
MAP_X = 16
MAP_Y = 16
MAP_W_PX = GRID_COLS * TILE_SIZE  # 800
MAP_H_PX = GRID_ROWS * TILE_SIZE  # 600

FPS = 60

# Colors
COLOR_BG = (30, 30, 40)
COLOR_PANEL = (45, 45, 60)
COLOR_BORDER = (100, 100, 120)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GOLD = (255, 193, 7)
COLOR_RED = (229, 57, 53)
COLOR_GREEN = (76, 175, 80)
COLOR_BLUE = (33, 150, 243)

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("大明王朝 RPG - 关卡与连接地图编辑器 (Ming Dynasty Map Editor)")
clock = pygame.time.Clock()

# Fonts
def get_font(size: int) -> pygame.font.Font:
    system_fonts = ["microsoftyahei", "simhei", "simsun", "stxihei", "dengxian"]
    for font_name in system_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            if font:
                return font
        except Exception:
            continue
    return pygame.font.Font(None, size)

font_small = get_font(14)
font_medium = get_font(18)
font_large = get_font(22)

# Load Tile Images & scale to 20x20
TILES_DIR = BASE_DIR / "assets" / "tiles"
PLAYER_DIR = BASE_DIR / "assets" / "player"
NPCS_DIR = BASE_DIR / "assets" / "npcs"

# Define all available tile keys and their paths
TILE_DEFS = {
    # Ground
    'g': ("普通草地", TILES_DIR / "01_草地" / "普通草地.png"),
    'f': ("带花草地", TILES_DIR / "01_草地" / "带小花的草地.png"),
    's': ("带石草地", TILES_DIR / "01_草地" / "带石块的草地.png"),
    'h': ("干草地", TILES_DIR / "01_草地" / "干草.png"),
    'r': ("石子路", TILES_DIR / "02_石子路" / "直石子路.png"),
    'c': ("弯石子路", TILES_DIR / "02_石子路" / "弯石子路.png"),
    'x': ("十字路口", TILES_DIR / "02_石子路" / "石子路交叉口.png"),
    'w': ("平静河面", TILES_DIR / "08_水域" / "平静的河面.png"),
    'o': ("波纹河水", TILES_DIR / "08_水域" / "有波纹的流动河水.png"),
    'a': ("浅水", TILES_DIR / "08_水域" / "有鹅卵石的浅水.png"),
    'd': ("深水", TILES_DIR / "08_水域" / "深水.png"),
    'b': ("木桥", TILES_DIR / "08_水域" / "有波纹的流动河水.png"), # Drawn custom in game, but we can show as water/bridge
    
    # Obstacles
    'T': ("橡树", TILES_DIR / "24_树木变体" / "橡树.png"),
    'P': ("松树", TILES_DIR / "24_树木变体" / "松树.png"),
    'M': ("枫树", TILES_DIR / "24_树木变体" / "枫树.png"),
    'K': ("枯树", TILES_DIR / "24_树木变体" / "枯树.png"),
    'F': ("村庄围栏", TILES_DIR / "07_村庄建筑" / "村庄围栏.png"),
    'J': ("村庄水井", TILES_DIR / "07_村庄建筑" / "村庄水井.png"),
    'S': ("木制路标", TILES_DIR / "10_互动道具" / "木制路标.png"),
    'B': ("篝火", TILES_DIR / "10_互动道具" / "篝火.png"),
    'U': ("木桶", TILES_DIR / "10_互动道具" / "木桶.png"),
    'X': ("破损木车", TILES_DIR / "10_互动道具" / "破损的木车.png"),
    'R': ("茅草屋顶", TILES_DIR / "07_村庄建筑" / "茅草屋顶.png"),
    'W': ("木墙", TILES_DIR / "07_村庄建筑" / "木墙.png"),
    'D': ("木门", TILES_DIR / "07_村庄建筑" / "木门.png"),
    'Y': ("小石碑", TILES_DIR / "10_互动道具" / "小石碑.png"),
    'C': ("宝箱", TILES_DIR / "18_废墟" / "废墟中的宝箱.png"),
    'm': ("麦田", TILES_DIR / "11_农田" / "整齐的麦田.png"),
    'i': ("稻田", TILES_DIR / "11_农田" / "稻田.png"),
    'v': ("菜地", TILES_DIR / "11_农田" / "菜地.png"),
    '.': ("空地 (Walkable)", None)
}

# Loaded textures
tile_images: dict[str, pygame.Surface] = {}
for char, (name, path) in TILE_DEFS.items():
    if path and path.exists():
        try:
            img = pygame.image.load(str(path)).convert_alpha()
            tile_images[char] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            print(f"Error loading {path}: {e}")
    if char not in tile_images:
        # Fallback colored surface
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        if char == '.':
            surf.fill((0, 0, 0, 0)) # Transparent
        elif char in ['g', 'f', 's', 'h']:
            surf.fill((50, 150, 50))
        elif char in ['r', 'c', 'x']:
            surf.fill((150, 150, 150))
        elif char in ['w', 'o', 'a', 'd']:
            surf.fill((50, 50, 200))
        else:
            surf.fill((200, 100, 50))
        tile_images[char] = surf

# Load NPC avatar
npc_avatar = pygame.Surface((TILE_SIZE, TILE_SIZE))
npc_avatar.fill(COLOR_GOLD)
pygame.draw.circle(npc_avatar, COLOR_BLACK, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//3, 2)

# Editor States
EDIT_LAYER_GROUND = 0
EDIT_LAYER_OBSTACLE = 1
EDIT_CONNECTIONS = 2

def format_python_literal(val, indent_level=0) -> str:
    spacing = " " * (indent_level * 4)
    if isinstance(val, dict):
        if not val:
            return "{}"
        lines = []
        for k, v in val.items():
            formatted_val = format_python_literal(v, indent_level + 1)
            lines.append(f"{spacing}    {repr(k)}: {formatted_val.lstrip()}")
        return "{\n" + ",\n".join(lines) + f"\n{spacing}}"
    elif isinstance(val, list):
        if not val:
            return "[]"
        if all(isinstance(x, (int, float, str)) for x in val) and len(str(val)) < 80:
            return "[" + ", ".join(repr(x) for x in val) + "]"
        lines = []
        for x in val:
            lines.append(f"{spacing}    {format_python_literal(x, indent_level + 1).lstrip()}")
        return "[\n" + ",\n".join(lines) + f"\n{spacing}]"
    elif isinstance(val, str):
        return repr(val)
    elif isinstance(val, bool):
        return "True" if val else "False"
    elif val is None:
        return "None"
    else:
        return str(val)

class MapEditor:
    def __init__(self) -> None:
        self.maps = {k: self.clone_map_data(v) for k, v in MAPS.items()}
        self.map_ids = list(self.maps.keys())
        self.current_map_id = "north"
        
        # UI selection state
        self.current_layer = EDIT_LAYER_GROUND
        self.selected_tile = 'g'
        self.selected_obstacle = '.'
        
        # Connection editing state
        self.selected_conn_dir = "south"
        self.conn_target_map = "south"
        self.conn_target_x = 14
        self.conn_target_y = 0
        
        # Mouse state
        self.is_painting = False

    def clone_map_data(self, original: dict) -> dict:
        """Deep clones map data to avoid modifying originals until saved."""
        return {
            "name": original["name"],
            "ground": [list(row) for row in original["ground"]],
            "obstacle": [list(row) for row in original["obstacle"]],
            "npcs": [dict(npc) for npc in original.get("npcs", [])],
            "chests": [dict(chest) for chest in original.get("chests", [])],
            "connections": {d: dict(conn) for d, conn in original.get("connections", {}).items()},
            "min_level": original.get("min_level", 1)
        }

    def get_current_map(self) -> dict:
        return self.maps[self.current_map_id]

    def save_all_data(self) -> None:
        """Saves edited maps back to map_data.py and scene JSONs."""
        # 1. Save JSON scenes
        for map_id, m_data in self.maps.items():
            # Skip static maps (north, south) for JSON output, or save them too?
            # Let's save all dynamic scenes to their JSONs
            json_path = SCENES_DIR / f"{map_id}.json"
            if json_path.exists() or map_id not in ["north", "south"]:
                scene_json = {
                    "name": m_data["name"],
                    "ground": ["".join(row) for row in m_data["ground"]],
                    "obstacle": ["".join(row) for row in m_data["obstacle"]],
                    "connections": m_data["connections"],
                    "npcs": m_data["npcs"],
                    "chests": m_data["chests"],
                    "min_level": m_data.get("min_level", 1)
                }
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(scene_json, f, ensure_ascii=False, indent=2)
                print(f"Saved scene JSON: {json_path}")

        # 2. Re-generate map_data.py
        self.write_map_data_py()
        print("Successfully updated map_data.py!")

    def write_map_data_py(self) -> None:
        """Saves the map data directly into map_data.py to persist changes."""
        py_path = BASE_DIR / "map_data.py"
        
        # Read the top and bottom of map_data.py, or just rewrite it cleanly
        # Writing it cleanly is much safer and more robust!
        content = []
        content.append("# -*- coding: utf-8 -*-")
        content.append("\"\"\"")
        content.append("Map data loader and registry for Ming Dynasty RPG.")
        content.append("Loads static maps (north, south) and dynamically loads historical scene JSON files.")
        content.append("GENERATED BY MAP EDITOR.")
        content.append("\"\"\"")
        content.append("")
        content.append("import json")
        content.append("from pathlib import Path")
        content.append("")
        content.append("MAP_WIDTH = 40")
        content.append("MAP_HEIGHT = 30")
        content.append("")
        content.append("BASE_DIR = Path(__file__).resolve().parent")
        content.append("SCENES_DIR = BASE_DIR / \"assets\" / \"scenes\"")
        content.append("")
        
        # Write North Map
        north = self.maps["north"]
        content.append("# ==========================================")
        content.append("# 1. 钟离县-北 (Zhongli County - North)")
        content.append("# ==========================================")
        content.append("")
        content.append("GROUND_MAP_NORTH = [")
        for row in north["ground"]:
            content.append(f"    \"{ ''.join(row) }\",")
        content.append("]")
        content.append("")
        content.append("OBSTACLE_MAP_NORTH = [")
        for row in north["obstacle"]:
            content.append(f"    \"{ ''.join(row) }\",")
        content.append("]")
        content.append("")
        
        # Write North NPCs
        content.append("NPCS_NORTH = " + format_python_literal(north["npcs"]))
        content.append("")
        # Write North Chests
        content.append("CHESTS_NORTH = " + format_python_literal(north["chests"]))
        content.append("")
        # Write North Connections
        content.append("CONNECTIONS_NORTH = " + format_python_literal(north["connections"]))
        content.append("")

        # Write South Map
        south = self.maps["south"]
        content.append("# ==========================================")
        content.append("# 2. 钟离县-南 (Zhongli County - South)")
        content.append("# ==========================================")
        content.append("")
        content.append("GROUND_MAP_SOUTH = [")
        for row in south["ground"]:
            content.append(f"    \"{ ''.join(row) }\",")
        content.append("]")
        content.append("")
        content.append("OBSTACLE_MAP_SOUTH = [")
        for row in south["obstacle"]:
            content.append(f"    \"{ ''.join(row) }\",")
        content.append("]")
        content.append("")
        
        # Write South NPCs
        content.append("NPCS_SOUTH = " + format_python_literal(south["npcs"]))
        content.append("")
        # Write South Chests
        content.append("CHESTS_SOUTH = " + format_python_literal(south["chests"]))
        content.append("")
        # Write South Connections
        content.append("CONNECTIONS_SOUTH = " + format_python_literal(south["connections"]))
        content.append("")

        # Write MAPS Registry
        content.append("# ==========================================")
        content.append("# 3. 场景注册表 (Scene Registry)")
        content.append("# ==========================================")
        content.append("")
        content.append("MAPS = {")
        content.append("    \"north\": {")
        content.append("        \"name\": \"濠州府 · 钟离县-北\",")
        content.append("        \"ground\": GROUND_MAP_NORTH,")
        content.append("        \"obstacle\": OBSTACLE_MAP_NORTH,")
        content.append("        \"npcs\": NPCS_NORTH,")
        content.append("        \"chests\": CHESTS_NORTH,")
        content.append("        \"connections\": CONNECTIONS_NORTH,")
        content.append(f"        \"min_level\": {north.get('min_level', 1)}")
        content.append("    },")
        content.append("    \"south\": {")
        content.append("        \"name\": \"濠州府 · 钟离县-南\",")
        content.append("        \"ground\": GROUND_MAP_SOUTH,")
        content.append("        \"obstacle\": OBSTACLE_MAP_SOUTH,")
        content.append("        \"npcs\": NPCS_SOUTH,")
        content.append("        \"chests\": CHESTS_SOUTH,")
        content.append("        \"connections\": CONNECTIONS_SOUTH,")
        content.append(f"        \"min_level\": {south.get('min_level', 1)}")
        content.append("    }")
        content.append("}")
        content.append("")
        
        # Write Dynamic Loader
        content.append("def load_dynamic_scenes() -> None:")
        content.append("    if SCENES_DIR.exists():")
        content.append("        for path in SCENES_DIR.glob(\"*.json\"):")
        content.append("            try:")
        content.append("                with open(path, \"r\", encoding=\"utf-8\") as f:")
        content.append("                    scene_data = json.load(f)")
        content.append("                    scene_id = path.stem")
        content.append("                    MAPS[scene_id] = scene_data")
        content.append("                    print(f\"Loaded dynamic scene: {scene_id} ({scene_data['name']})\")")
        content.append("            except Exception as e:")
        content.append("                print(f\"Error loading scene {path}: {e}\")")
        content.append("")
        content.append("load_dynamic_scenes()")
        
        with open(py_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

    def handle_mouse_paint(self, mouse_pos: tuple[int, int]) -> None:
        mx, my = mouse_pos
        # Check if inside map coordinates
        if MAP_X <= mx < MAP_X + MAP_W_PX and MAP_Y <= my < MAP_Y + MAP_H_PX:
            col = (mx - MAP_X) // TILE_SIZE
            row = (my - MAP_Y) // TILE_SIZE
            
            m_data = self.get_current_map()
            if self.current_layer == EDIT_LAYER_GROUND:
                m_data["ground"][row][col] = self.selected_tile
            elif self.current_layer == EDIT_LAYER_OBSTACLE:
                m_data["obstacle"][row][col] = self.selected_obstacle

    def draw(self) -> None:
        screen.fill(COLOR_BG)
        
        # 1. Draw Map Grid
        m_data = self.get_current_map()
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                tx = MAP_X + c * TILE_SIZE
                ty = MAP_Y + r * TILE_SIZE
                
                # Draw Ground
                g_char = m_data["ground"][r][c]
                screen.blit(tile_images[g_char], (tx, ty))
                
                # Draw Obstacle
                o_char = m_data["obstacle"][r][c]
                if o_char != '.':
                    screen.blit(tile_images[o_char], (tx, ty))
                    
        # Draw grid lines (subtle)
        for r in range(GRID_ROWS + 1):
            pygame.draw.line(screen, (50, 50, 65), (MAP_X, MAP_Y + r * TILE_SIZE), (MAP_X + MAP_W_PX, MAP_Y + r * TILE_SIZE))
        for c in range(GRID_COLS + 1):
            pygame.draw.line(screen, (50, 50, 65), (MAP_X + c * TILE_SIZE, MAP_Y), (MAP_X + c * TILE_SIZE, MAP_Y + MAP_H_PX))
            
        # Draw NPCs
        for npc in m_data["npcs"]:
            nx = MAP_X + npc["x"] * TILE_SIZE
            ny = MAP_Y + npc["y"] * TILE_SIZE
            screen.blit(npc_avatar, (nx, ny))
            # Draw tiny name tag
            name_surf = font_small.render(npc["name"][:2], True, COLOR_GOLD)
            screen.blit(name_surf, (nx, ny - 10))

        # Draw map outline border
        pygame.draw.rect(screen, COLOR_BORDER, (MAP_X, MAP_Y, MAP_W_PX, MAP_H_PX), 2)

        # 2. Draw Right Panel (Controls & Palette)
        panel_x = MAP_X + MAP_W_PX + 16
        panel_w = SCREEN_WIDTH - panel_x - 16
        panel_rect = pygame.Rect(panel_x, MAP_Y, panel_w, MAP_H_PX)
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect)
        pygame.draw.rect(screen, COLOR_BORDER, panel_rect, 2)
        
        # Map Selection Dropdown / Selector
        title_surf = font_large.render("大明地图编辑器", True, COLOR_GOLD)
        screen.blit(title_surf, (panel_x + 12, MAP_Y + 12))
        
        map_sel_title = font_medium.render(f"当前地图: {m_data['name']}", True, COLOR_WHITE)
        screen.blit(map_sel_title, (panel_x + 12, MAP_Y + 45))
        
        # Button: Switch Map (Next)
        btn_next_map = pygame.Rect(panel_x + 12, MAP_Y + 70, panel_w - 24, 25)
        pygame.draw.rect(screen, COLOR_BLUE, btn_next_map)
        btn_text = font_small.render("切换到下一个场景 (Tab)", True, COLOR_WHITE)
        screen.blit(btn_text, (btn_next_map.x + 10, btn_next_map.y + 5))
        
        # Layer Selector
        layer_title = font_medium.render("编辑图层:", True, COLOR_WHITE)
        screen.blit(layer_title, (panel_x + 12, MAP_Y + 110))
        
        # Layer Buttons
        layers = [
            (EDIT_LAYER_GROUND, "地表层 (1)", COLOR_GREEN if self.current_layer == EDIT_LAYER_GROUND else (80, 80, 80)),
            (EDIT_LAYER_OBSTACLE, "障碍层 (2)", COLOR_GREEN if self.current_layer == EDIT_LAYER_OBSTACLE else (80, 80, 80)),
            (EDIT_CONNECTIONS, "连接管理 (3)", COLOR_GREEN if self.current_layer == EDIT_CONNECTIONS else (80, 80, 80))
        ]
        for idx, (layer_id, label, col) in enumerate(layers):
            btn_rect = pygame.Rect(panel_x + 12 + idx * 80, MAP_Y + 135, 75, 25)
            pygame.draw.rect(screen, col, btn_rect)
            lbl_surf = font_small.render(label, True, COLOR_WHITE)
            screen.blit(lbl_surf, (btn_rect.x + 5, btn_rect.y + 5))

        # Palette / Connection Details
        if self.current_layer == EDIT_LAYER_GROUND:
            pal_title = font_medium.render("地表图块调色板:", True, COLOR_WHITE)
            screen.blit(pal_title, (panel_x + 12, MAP_Y + 175))
            
            # List ground tiles
            ground_chars = ['g', 'f', 's', 'h', 'r', 'c', 'x', 'w', 'o', 'a', 'd', 'b']
            for idx, char in enumerate(ground_chars):
                bx = panel_x + 12 + (idx % 4) * 55
                by = MAP_Y + 200 + (idx // 4) * 45
                btn_rect = pygame.Rect(bx, by, 45, 42)
                
                # Draw selection highlight
                border_col = COLOR_GOLD if self.selected_tile == char else COLOR_BORDER
                pygame.draw.rect(screen, border_col, btn_rect, 2)
                
                # Draw tile preview
                screen.blit(tile_images[char], (bx + 12, by + 3))
                lbl = font_small.render(TILE_DEFS[char][0][:2], True, COLOR_WHITE)
                lbl_x = bx + (45 - lbl.get_width()) // 2
                screen.blit(lbl, (lbl_x, by + 24))
                
        elif self.current_layer == EDIT_LAYER_OBSTACLE:
            pal_title = font_medium.render("障碍图块调色板:", True, COLOR_WHITE)
            screen.blit(pal_title, (panel_x + 12, MAP_Y + 175))
            
            # List obstacle tiles
            obstacle_chars = ['T', 'P', 'M', 'K', 'F', 'J', 'S', 'B', 'U', 'X', 'R', 'W', 'D', 'Y', 'C', 'm', 'i', 'v', '.']
            for idx, char in enumerate(obstacle_chars):
                bx = panel_x + 12 + (idx % 4) * 55
                by = MAP_Y + 200 + (idx // 4) * 45
                btn_rect = pygame.Rect(bx, by, 45, 42)
                
                # Draw selection highlight
                border_col = COLOR_GOLD if self.selected_obstacle == char else COLOR_BORDER
                pygame.draw.rect(screen, border_col, btn_rect, 2)
                
                # Draw tile preview
                if char != '.':
                    screen.blit(tile_images[char], (bx + 12, by + 3))
                lbl = font_small.render(TILE_DEFS[char][0][:2], True, COLOR_WHITE)
                lbl_x = bx + (45 - lbl.get_width()) // 2
                screen.blit(lbl, (lbl_x, by + 24))
                
        elif self.current_layer == EDIT_CONNECTIONS:
            conn_title = font_medium.render("地图边界连接信息:", True, COLOR_WHITE)
            screen.blit(conn_title, (panel_x + 12, MAP_Y + 175))
            
            # Show existing connections
            conns = m_data.get("connections", {})
            cy = MAP_Y + 200
            for direction in ["north", "south", "west", "east"]:
                conn_info = conns.get(direction)
                if conn_info:
                    txt = f"{direction.upper()}: -> {conn_info['map_id']} ({conn_info['start_x']},{conn_info['start_y']})"
                    col = COLOR_GOLD
                else:
                    txt = f"{direction.upper()}: 无连接"
                    col = (150, 150, 150)
                txt_surf = font_small.render(txt, True, col)
                screen.blit(txt_surf, (panel_x + 12, cy))
                cy += 20

            # Scene Entry Level limit configuration
            lvl_title = font_small.render("进入等级限制:", True, COLOR_WHITE)
            screen.blit(lvl_title, (panel_x + 12, MAP_Y + 285))
            
            # Draw [-] button
            btn_minus = pygame.Rect(panel_x + 115, MAP_Y + 282, 25, 20)
            pygame.draw.rect(screen, (80, 80, 80), btn_minus)
            pygame.draw.rect(screen, COLOR_BORDER, btn_minus, 1)
            minus_txt = font_small.render("-", True, COLOR_WHITE)
            screen.blit(minus_txt, (btn_minus.x + 9, btn_minus.y + 2))
            
            # Current level value text
            cur_lvl = m_data.get("min_level", 1)
            lvl_val_txt = font_medium.render(str(cur_lvl), True, COLOR_GOLD)
            screen.blit(lvl_val_txt, (panel_x + 152, MAP_Y + 283))
            
            # Draw [+] button
            btn_plus = pygame.Rect(panel_x + 180, MAP_Y + 282, 25, 20)
            pygame.draw.rect(screen, (80, 80, 80), btn_plus)
            pygame.draw.rect(screen, COLOR_BORDER, btn_plus, 1)
            plus_txt = font_small.render("+", True, COLOR_WHITE)
            screen.blit(plus_txt, (btn_plus.x + 7, btn_plus.y + 2))
                
            # Connection Editor Panel
            edit_title = font_medium.render("编辑选中方向连接:", True, COLOR_WHITE)
            screen.blit(edit_title, (panel_x + 12, MAP_Y + 310))
            
            # Direction Buttons
            dirs = ["north", "south", "west", "east"]
            for idx, d in enumerate(dirs):
                bx = panel_x + 12 + idx * 55
                by = MAP_Y + 335
                btn_rect = pygame.Rect(bx, by, 50, 25)
                col = COLOR_BLUE if self.selected_conn_dir == d else (80, 80, 80)
                pygame.draw.rect(screen, col, btn_rect)
                lbl = font_small.render(d.upper()[:5], True, COLOR_WHITE)
                screen.blit(lbl, (btn_rect.x + 5, btn_rect.y + 5))
                
            # Current value and inputs
            cur_conn = conns.get(self.selected_conn_dir, {"map_id": "none", "start_x": 0, "start_y": 0})
            val_txt = f"目标地图: {cur_conn['map_id']}"
            val_surf = font_small.render(val_txt, True, COLOR_WHITE)
            screen.blit(val_surf, (panel_x + 12, MAP_Y + 375))
            
            coord_txt = f"出生点坐标: ({cur_conn['start_x']}, {cur_conn['start_y']})"
            coord_surf = font_small.render(coord_txt, True, COLOR_WHITE)
            screen.blit(coord_surf, (panel_x + 12, MAP_Y + 395))
            
            # Quick presets
            preset_title = font_small.render("快速预设连接目标 (点击修改):", True, COLOR_GOLD)
            screen.blit(preset_title, (panel_x + 12, MAP_Y + 425))
            
            # List other maps as buttons to quickly link
            other_maps = [m for m in self.map_ids if m != self.current_map_id][:6]
            for idx, om in enumerate(other_maps):
                bx = panel_x + 12 + (idx % 2) * 110
                by = MAP_Y + 445 + (idx // 2) * 30
                btn_rect = pygame.Rect(bx, by, 100, 25)
                pygame.draw.rect(screen, (70, 70, 90), btn_rect)
                pygame.draw.rect(screen, COLOR_BORDER, btn_rect, 1)
                lbl = font_small.render(om[:12], True, COLOR_WHITE)
                screen.blit(lbl, (btn_rect.x + 5, btn_rect.y + 5))

        # Save Button at the bottom of panel
        btn_save = pygame.Rect(panel_x + 12, MAP_Y + 540, panel_w - 24, 40)
        pygame.draw.rect(screen, COLOR_RED, btn_save)
        
        # Ensure text is dynamically centered and doesn't spill out of the button
        save_text = font_medium.render("💾 保存修改 (Save to .py)", True, COLOR_WHITE)
        if save_text.get_width() > btn_save.width - 10:
            save_text = font_small.render("💾 保存修改 (Save to .py)", True, COLOR_WHITE)
            
        text_x = btn_save.x + (btn_save.width - save_text.get_width()) // 2
        text_y = btn_save.y + (btn_save.height - save_text.get_height()) // 2
        screen.blit(save_text, (text_x, text_y))

        # 3. Draw Bottom Status Bar
        status_rect = pygame.Rect(MAP_X, MAP_Y + MAP_H_PX + 12, SCREEN_WIDTH - MAP_X * 2, 40)
        pygame.draw.rect(screen, COLOR_PANEL, status_rect)
        pygame.draw.rect(screen, COLOR_BORDER, status_rect, 2)
        
        status_text = (
            f"操作提示: [左键] 绘制/选择 | [1] 地表层 | [2] 障碍层 | [3] 连接层 | "
            f"[Tab] 切换地图 | [S] 键盘快捷保存"
        )
        status_surf = font_medium.render(status_text, True, COLOR_GOLD)
        screen.blit(status_surf, (status_rect.x + 15, status_rect.y + 10))

    def run(self) -> None:
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.current_layer = EDIT_LAYER_GROUND
                    elif event.key == pygame.K_2:
                        self.current_layer = EDIT_LAYER_OBSTACLE
                    elif event.key == pygame.K_3:
                        self.current_layer = EDIT_CONNECTIONS
                    elif event.key == pygame.K_TAB:
                        # Switch to next map
                        idx = self.map_ids.index(self.current_map_id)
                        self.current_map_id = self.map_ids[(idx + 1) % len(self.map_ids)]
                    elif event.key == pygame.K_s:
                        # Quick save
                        self.save_all_data()
                        play_beep = lambda f, d: None # Silently save
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mx, my = event.pos
                        panel_x = MAP_X + MAP_W_PX + 16
                        panel_w = SCREEN_WIDTH - panel_x - 16
                        
                        # 1. Check if clicked inside map area
                        if MAP_X <= mx < MAP_X + MAP_W_PX and MAP_Y <= my < MAP_Y + MAP_H_PX:
                            self.is_painting = True
                            self.handle_mouse_paint(event.pos)
                            
                        # 2. Check if clicked Next Map Button
                        elif panel_x + 12 <= mx < panel_x + panel_w - 12 and MAP_Y + 70 <= my < MAP_Y + 95:
                            idx = self.map_ids.index(self.current_map_id)
                            self.current_map_id = self.map_ids[(idx + 1) % len(self.map_ids)]
                            
                        # 3. Check Layer Buttons
                        elif MAP_Y + 135 <= my < MAP_Y + 160:
                            for idx in range(3):
                                bx = panel_x + 12 + idx * 80
                                if bx <= mx < bx + 75:
                                    self.current_layer = idx
                                    
                        # 4. Check Palette / Connection Editor clicks
                        elif self.current_layer == EDIT_LAYER_GROUND:
                            ground_chars = ['g', 'f', 's', 'h', 'r', 'c', 'x', 'w', 'o', 'a', 'd', 'b']
                            for idx, char in enumerate(ground_chars):
                                bx = panel_x + 12 + (idx % 4) * 55
                                by = MAP_Y + 200 + (idx // 4) * 45
                                if bx <= mx < bx + 45 and by <= my < by + 42:
                                    self.selected_tile = char
                                    
                        elif self.current_layer == EDIT_LAYER_OBSTACLE:
                            obstacle_chars = ['T', 'P', 'M', 'K', 'F', 'J', 'S', 'B', 'U', 'X', 'R', 'W', 'D', 'Y', 'C', 'm', 'i', 'v', '.']
                            for idx, char in enumerate(obstacle_chars):
                                bx = panel_x + 12 + (idx % 4) * 55
                                by = MAP_Y + 200 + (idx // 4) * 45
                                if bx <= mx < bx + 45 and by <= my < by + 42:
                                    self.selected_obstacle = char
                                    
                        elif self.current_layer == EDIT_CONNECTIONS:
                            # Check Entry Level Limit [-] and [+] buttons
                            btn_minus = pygame.Rect(panel_x + 115, MAP_Y + 282, 25, 20)
                            btn_plus = pygame.Rect(panel_x + 180, MAP_Y + 282, 25, 20)
                            m_data = self.get_current_map()
                            current_min_lvl = m_data.get("min_level", 1)
                            
                            if btn_minus.collidepoint(mx, my):
                                if current_min_lvl > 1:
                                    m_data["min_level"] = current_min_lvl - 1
                            elif btn_plus.collidepoint(mx, my):
                                m_data["min_level"] = current_min_lvl + 1
                                
                            # Check Direction Buttons
                            elif MAP_Y + 335 <= my < MAP_Y + 360:
                                dirs = ["north", "south", "west", "east"]
                                for idx, d in enumerate(dirs):
                                    bx = panel_x + 12 + idx * 55
                                    if bx <= mx < bx + 50:
                                        self.selected_conn_dir = d
                                        
                            # Check Preset Targets
                            elif MAP_Y + 445 <= my < MAP_Y + 535:
                                other_maps = [m for m in self.map_ids if m != self.current_map_id][:6]
                                for idx, om in enumerate(other_maps):
                                    bx = panel_x + 12 + (idx % 2) * 110
                                    by = MAP_Y + 445 + (idx // 2) * 30
                                    if bx <= mx < bx + 100 and by <= my < by + 25:
                                        # Set connection target for selected direction
                                        m_data = self.get_current_map()
                                        # Set default transition coordinates based on direction
                                        start_x, start_y = 14, 15
                                        if self.selected_conn_dir == "north":
                                            start_x, start_y = 14, 28
                                        elif self.selected_conn_dir == "south":
                                            start_x, start_y = 14, 1
                                        elif self.selected_conn_dir == "west":
                                            start_x, start_y = 38, 15
                                        elif self.selected_conn_dir == "east":
                                            start_x, start_y = 1, 15
                                            
                                        m_data["connections"][self.selected_conn_dir] = {
                                            "map_id": om,
                                            "start_x": start_x,
                                            "start_y": start_y
                                        }
                                        
                        # 5. Check Save Button
                        if panel_x + 12 <= mx < panel_x + panel_w - 12 and MAP_Y + 540 <= my < MAP_Y + 580:
                            self.save_all_data()
                            
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_painting = False
                        
                elif event.type == pygame.MOUSEMOTION:
                    if self.is_painting:
                        self.handle_mouse_paint(event.pos)

            # Draw everything
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    print("==================================================")
    print("  大明王朝 RPG - 地图与连接可视化编辑器")
    print("  启动中...")
    print("==================================================")
    editor = MapEditor()
    editor.run()
