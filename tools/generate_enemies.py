"""
Generate Yuan Dynasty enemies (soldiers, mini-bosses, and ultimate boss) sprites in 4 directions (down, up, left, right).
Each sprite is 32x32 pixels, using a retro 8-bit NES style.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

TILE = 32
OUT = Path(__file__).resolve().parent.parent / "assets" / "enemies"
OUT.mkdir(parents=True, exist_ok=True)

# Colors
SKIN = (240, 200, 160)
SKIN_SHADOW = (200, 150, 110)
EYE = (0, 0, 0)
SHOE = (50, 50, 50)

# Soldier Colors (Red/Grey)
SOLDIER_TUNIC = (160, 35, 35)
SOLDIER_TUNIC_DARK = (110, 20, 20)
SOLDIER_HELMET = (110, 115, 125)
SOLDIER_HELMET_SHINE = (170, 180, 190)
SOLDIER_TASSEL = (230, 50, 50)
SOLDIER_BELT = (90, 60, 40)
METAL_BLADE = (180, 185, 195)
METAL_HILT = (210, 160, 50)

# Boss Colors (Purple/Gold)
BOSS_TUNIC = (90, 30, 130)
BOSS_TUNIC_DARK = (60, 15, 90)
BOSS_HELMET = (215, 165, 40) # Golden helmet
BOSS_HELMET_SHINE = (255, 230, 130)
BOSS_TASSEL = (240, 40, 40)
BOSS_CAPE = (180, 30, 30)

# Emperor Colors (Imperial Gold/Red)
EMP_TUNIC = (235, 185, 30) # Imperial Gold
EMP_TUNIC_DARK = (180, 135, 15)
EMP_CROWN = (245, 215, 50)
EMP_CROWN_JEWEL = (230, 40, 40)
EMP_CAPE = (190, 25, 25)
EMP_CAPE_DARK = (130, 15, 15)
EMP_FUR = (245, 245, 245)

def create_base_sprite() -> Image.Image:
    return Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))

# ==========================================
# 1. YUAN SOLDIER
# ==========================================

def draw_soldier_down(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((10, foot_y - 2, 13, 30), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    else:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y - 2, 21, 30), fill=SHOE)

    # Tunic / Armor
    d.rectangle((8, 14, 23, 28), fill=SOLDIER_TUNIC)
    d.rectangle((8, 26, 23, 28), fill=SOLDIER_TUNIC_DARK)
    d.rectangle((8, 20, 23, 21), fill=SOLDIER_BELT) # Belt
    
    # Head
    d.ellipse((10, 6, 21, 16), fill=SKIN)
    
    # Helmet
    d.ellipse((10, 3, 21, 10), fill=SOLDIER_HELMET)
    d.rectangle((14, 1, 17, 4), fill=SOLDIER_HELMET) # Pointy top
    d.rectangle((15, 0, 16, 1), fill=SOLDIER_TASSEL) # Red tassel
    d.point((12, 5), fill=SOLDIER_HELMET_SHINE)
    
    # Eyes
    d.rectangle((12, 10, 13, 12), fill=EYE)
    d.rectangle((18, 10, 19, 12), fill=EYE)
    
    # Weapon (Spear/Halberd in right hand)
    # Hand
    d.rectangle((22, 17, 24, 19), fill=SKIN)
    # Spear shaft (brown)
    d.line([(23, 8), (23, 28)], fill=SOLDIER_BELT, width=1)
    # Spear head (metal)
    d.polygon([(22, 7), (24, 7), (23, 3)], fill=METAL_BLADE)
    d.point((23, 2), fill=SOLDIER_TASSEL) # Small red tassel on spear
    
    return img

def draw_soldier_up(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((10, foot_y - 2, 13, 30), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    else:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y - 2, 21, 30), fill=SHOE)

    # Tunic (Back view)
    d.rectangle((8, 14, 23, 28), fill=SOLDIER_TUNIC)
    d.rectangle((8, 26, 23, 28), fill=SOLDIER_TUNIC_DARK)
    d.rectangle((8, 20, 23, 21), fill=SOLDIER_BELT)
    
    # Head & Helmet
    d.ellipse((10, 6, 21, 16), fill=SKIN_SHADOW)
    d.ellipse((10, 3, 21, 10), fill=SOLDIER_HELMET)
    d.rectangle((14, 1, 17, 4), fill=SOLDIER_HELMET)
    d.rectangle((15, 0, 16, 1), fill=SOLDIER_TASSEL)
    
    # Spear on back/left hand
    d.rectangle((7, 17, 9, 19), fill=SKIN_SHADOW)
    d.line([(8, 8), (8, 28)], fill=SOLDIER_BELT, width=1)
    d.polygon([(7, 7), (9, 7), (8, 3)], fill=METAL_BLADE)
    
    return img

def draw_soldier_left(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((11, foot_y - 2, 14, 30), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    else:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y - 2, 20, 30), fill=SHOE)

    # Tunic
    d.rectangle((9, 14, 22, 28), fill=SOLDIER_TUNIC)
    d.rectangle((9, 26, 22, 28), fill=SOLDIER_TUNIC_DARK)
    d.rectangle((9, 20, 22, 21), fill=SOLDIER_BELT)
    
    # Head & Helmet
    d.ellipse((10, 6, 21, 16), fill=SKIN)
    d.ellipse((10, 3, 21, 10), fill=SOLDIER_HELMET)
    d.rectangle((14, 1, 17, 4), fill=SOLDIER_HELMET)
    d.rectangle((15, 0, 16, 1), fill=SOLDIER_TASSEL)
    
    # Eye
    d.rectangle((12, 10, 13, 12), fill=EYE)
    
    # Spear in left hand
    d.rectangle((6, 17, 8, 19), fill=SKIN)
    d.line([(7, 8), (7, 28)], fill=SOLDIER_BELT, width=1)
    d.polygon([(6, 7), (8, 7), (7, 3)], fill=METAL_BLADE)
    
    return img

def draw_soldier_right(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((11, foot_y - 2, 14, 30), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    else:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y - 2, 20, 30), fill=SHOE)

    # Tunic
    d.rectangle((9, 14, 22, 28), fill=SOLDIER_TUNIC)
    d.rectangle((9, 26, 22, 28), fill=SOLDIER_TUNIC_DARK)
    d.rectangle((9, 20, 22, 21), fill=SOLDIER_BELT)
    
    # Head & Helmet
    d.ellipse((10, 6, 21, 16), fill=SKIN)
    d.ellipse((10, 3, 21, 10), fill=SOLDIER_HELMET)
    d.rectangle((13, 1, 16, 4), fill=SOLDIER_HELMET)
    d.rectangle((14, 0, 15, 1), fill=SOLDIER_TASSEL)
    
    # Eye
    d.rectangle((18, 10, 19, 12), fill=EYE)
    
    # Spear in right hand
    d.rectangle((23, 17, 25, 19), fill=SKIN)
    d.line([(24, 8), (24, 28)], fill=SOLDIER_BELT, width=1)
    d.polygon([(23, 7), (25, 7), (24, 3)], fill=METAL_BLADE)
    
    return img


# ==========================================
# 2. MINI-BOSS (YUAN CAPTAIN)
# ==========================================

def draw_boss_down(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Cape (back layer)
    d.rectangle((6, 15, 25, 28), fill=BOSS_CAPE)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((10, foot_y - 2, 13, 30), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    else:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y - 2, 21, 30), fill=SHOE)

    # Tunic / Heavy Armor
    d.rectangle((8, 13, 23, 28), fill=BOSS_TUNIC)
    d.rectangle((8, 25, 23, 28), fill=BOSS_TUNIC_DARK)
    # Golden shoulder pads
    d.rectangle((7, 13, 10, 16), fill=BOSS_HELMET)
    d.rectangle((21, 13, 24, 16), fill=BOSS_HELMET)
    # Golden Belt
    d.rectangle((8, 20, 23, 22), fill=BOSS_HELMET)
    d.point((15, 21), fill=BOSS_TASSEL) # Red gem on belt
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Golden Helmet
    d.ellipse((10, 2, 21, 9), fill=BOSS_HELMET)
    d.rectangle((14, 0, 17, 3), fill=BOSS_HELMET) # Pointy top
    d.ellipse((13, -2, 18, 1), fill=BOSS_TASSEL) # Large red plume
    d.point((12, 4), fill=BOSS_HELMET_SHINE)
    
    # Eyes
    d.rectangle((12, 9, 13, 11), fill=EYE)
    d.rectangle((18, 9, 19, 11), fill=EYE)
    
    # Big Broadsword in right hand
    # Hand
    d.rectangle((24, 16, 26, 18), fill=SKIN)
    # Sword hilt
    d.line([(25, 14), (25, 19)], fill=METAL_HILT, width=1)
    # Sword blade (large)
    d.rectangle((24, 4, 26, 13), fill=METAL_BLADE)
    d.point((25, 3), fill=METAL_BLADE)
    
    return img

def draw_boss_up(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Cape (covers back)
    d.rectangle((6, 13, 25, 28), fill=BOSS_CAPE)
    d.rectangle((7, 26, 24, 28), fill=(130, 20, 20)) # Cape shadow
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((10, foot_y - 2, 13, 30), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    else:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y - 2, 21, 30), fill=SHOE)

    # Golden shoulder pads (visible from back)
    d.rectangle((7, 13, 10, 16), fill=BOSS_HELMET)
    d.rectangle((21, 13, 24, 16), fill=BOSS_HELMET)
    
    # Head & Golden Helmet
    d.ellipse((10, 5, 21, 15), fill=SKIN_SHADOW)
    d.ellipse((10, 2, 21, 9), fill=BOSS_HELMET)
    d.rectangle((14, 0, 17, 3), fill=BOSS_HELMET)
    d.ellipse((13, -2, 18, 1), fill=BOSS_TASSEL)
    
    # Sword on back
    d.rectangle((24, 4, 26, 13), fill=METAL_BLADE)
    d.line([(25, 14), (25, 19)], fill=METAL_HILT, width=1)
    
    return img

def draw_boss_left(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Cape
    d.rectangle((16, 14, 23, 28), fill=BOSS_CAPE)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((11, foot_y - 2, 14, 30), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    else:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y - 2, 20, 30), fill=SHOE)

    # Tunic / Heavy Armor
    d.rectangle((9, 13, 21, 28), fill=BOSS_TUNIC)
    d.rectangle((9, 25, 21, 28), fill=BOSS_TUNIC_DARK)
    # Shoulder pad
    d.rectangle((13, 13, 17, 16), fill=BOSS_HELMET)
    # Belt
    d.rectangle((9, 20, 21, 22), fill=BOSS_HELMET)
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Golden Helmet
    d.ellipse((10, 2, 21, 9), fill=BOSS_HELMET)
    d.rectangle((14, 0, 17, 3), fill=BOSS_HELMET)
    d.ellipse((13, -2, 18, 1), fill=BOSS_TASSEL)
    
    # Eye
    d.rectangle((12, 9, 13, 11), fill=EYE)
    
    # Broadsword in left hand
    d.rectangle((6, 16, 8, 18), fill=SKIN)
    d.line([(7, 14), (7, 19)], fill=METAL_HILT, width=1)
    d.rectangle((6, 4, 8, 13), fill=METAL_BLADE)
    d.point((7, 3), fill=METAL_BLADE)
    
    return img

def draw_boss_right(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Cape
    d.rectangle((8, 14, 15, 28), fill=BOSS_CAPE)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((11, foot_y - 2, 14, 30), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    else:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y - 2, 20, 30), fill=SHOE)

    # Tunic / Heavy Armor
    d.rectangle((10, 13, 22, 28), fill=BOSS_TUNIC)
    d.rectangle((10, 25, 22, 28), fill=BOSS_TUNIC_DARK)
    # Shoulder pad
    d.rectangle((14, 13, 18, 16), fill=BOSS_HELMET)
    # Belt
    d.rectangle((10, 20, 22, 22), fill=BOSS_HELMET)
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Golden Helmet
    d.ellipse((10, 2, 21, 9), fill=BOSS_HELMET)
    d.rectangle((14, 0, 17, 3), fill=BOSS_HELMET)
    d.ellipse((13, -2, 18, 1), fill=BOSS_TASSEL)
    
    # Eye
    d.rectangle((18, 9, 19, 11), fill=EYE)
    
    # Broadsword in right hand
    d.rectangle((23, 16, 25, 18), fill=SKIN)
    d.line([(24, 14), (24, 19)], fill=METAL_HILT, width=1)
    d.rectangle((23, 4, 25, 13), fill=METAL_BLADE)
    d.point((24, 3), fill=METAL_BLADE)
    
    return img


# ==========================================
# 3. ULTIMATE BOSS (YUAN EMPEROR)
# ==========================================

def draw_emperor_down(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Grand Imperial Cape
    d.rectangle((4, 12, 27, 28), fill=EMP_CAPE)
    d.rectangle((4, 26, 27, 28), fill=EMP_CAPE_DARK)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((10, foot_y - 2, 13, 30), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    else:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y - 2, 21, 30), fill=SHOE)

    # Imperial Golden Robe
    d.rectangle((7, 12, 24, 28), fill=EMP_TUNIC)
    d.rectangle((7, 25, 24, 28), fill=EMP_TUNIC_DARK)
    # White Fur trim on robe edges
    d.rectangle((7, 12, 24, 14), fill=EMP_FUR)
    d.rectangle((14, 14, 17, 28), fill=EMP_FUR) # Middle fur sash
    # Crown jewels / belt
    d.rectangle((8, 20, 23, 22), fill=EMP_CROWN)
    d.point((15, 21), fill=EMP_CROWN_JEWEL)
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Imperial Crown (Mongol High Hat style)
    d.polygon([(11, 4), (20, 4), (17, -1), (14, -1)], fill=EMP_CROWN)
    d.rectangle((10, 2, 21, 5), fill=EMP_FUR) # Fur brim
    d.ellipse((14, -3, 17, 0), fill=EMP_CROWN_JEWEL) # Big ruby on top
    
    # Eyes
    d.rectangle((12, 9, 13, 11), fill=EYE)
    d.rectangle((18, 9, 19, 11), fill=EYE)
    
    # Legendary Golden Sabre in right hand
    # Hand
    d.rectangle((24, 16, 26, 18), fill=SKIN)
    # Sabre hilt
    d.line([(25, 14), (25, 19)], fill=EMP_CROWN_JEWEL, width=1)
    # Sabre blade (curved, golden/shining)
    d.rectangle((24, 4, 26, 13), fill=EMP_CROWN)
    d.point((25, 3), fill=EMP_CROWN)
    
    return img

def draw_emperor_up(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Cape covers everything
    d.rectangle((4, 12, 27, 28), fill=EMP_CAPE)
    d.rectangle((4, 25, 27, 28), fill=EMP_CAPE_DARK)
    d.rectangle((6, 12, 25, 14), fill=EMP_FUR) # Fur collar on back
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((10, foot_y - 2, 13, 30), fill=SHOE)
        d.rectangle((18, foot_y, 21, 31), fill=SHOE)
    else:
        d.rectangle((10, foot_y, 13, 31), fill=SHOE)
        d.rectangle((18, foot_y - 2, 21, 30), fill=SHOE)

    # Head & Crown (Back view)
    d.ellipse((10, 5, 21, 15), fill=SKIN_SHADOW)
    d.polygon([(11, 4), (20, 4), (17, -1), (14, -1)], fill=EMP_CROWN)
    d.rectangle((10, 2, 21, 5), fill=EMP_FUR)
    d.ellipse((14, -3, 17, 0), fill=EMP_CROWN_JEWEL)
    
    return img

def draw_emperor_left(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Cape
    d.rectangle((17, 12, 25, 28), fill=EMP_CAPE)
    d.rectangle((17, 25, 25, 28), fill=EMP_CAPE_DARK)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((11, foot_y - 2, 14, 30), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    else:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y - 2, 20, 30), fill=SHOE)

    # Imperial Robe
    d.rectangle((9, 12, 20, 28), fill=EMP_TUNIC)
    d.rectangle((9, 25, 20, 28), fill=EMP_TUNIC_DARK)
    d.rectangle((9, 12, 20, 14), fill=EMP_FUR) # Fur trim
    d.rectangle((9, 20, 20, 22), fill=EMP_CROWN) # Belt
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Crown
    d.polygon([(11, 4), (20, 4), (17, -1), (14, -1)], fill=EMP_CROWN)
    d.rectangle((10, 2, 21, 5), fill=EMP_FUR)
    d.ellipse((14, -3, 17, 0), fill=EMP_CROWN_JEWEL)
    
    # Eye
    d.rectangle((12, 9, 13, 11), fill=EYE)
    
    # Golden Sabre in left hand
    d.rectangle((6, 16, 8, 18), fill=SKIN)
    d.line([(7, 14), (7, 19)], fill=EMP_CROWN_JEWEL, width=1)
    d.rectangle((6, 4, 8, 13), fill=EMP_CROWN)
    d.point((7, 3), fill=EMP_CROWN)
    
    return img

def draw_emperor_right(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Cape
    d.rectangle((7, 12, 15, 28), fill=EMP_CAPE)
    d.rectangle((7, 25, 15, 28), fill=EMP_CAPE_DARK)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((11, foot_y - 2, 14, 30), fill=SHOE)
        d.rectangle((17, foot_y, 20, 31), fill=SHOE)
    else:
        d.rectangle((11, foot_y, 14, 31), fill=SHOE)
        d.rectangle((17, foot_y - 2, 20, 30), fill=SHOE)

    # Imperial Robe
    d.rectangle((12, 12, 23, 28), fill=EMP_TUNIC)
    d.rectangle((12, 25, 23, 28), fill=EMP_TUNIC_DARK)
    d.rectangle((12, 12, 23, 14), fill=EMP_FUR) # Fur trim
    d.rectangle((12, 20, 23, 22), fill=EMP_CROWN) # Belt
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Crown
    d.polygon([(11, 4), (20, 4), (17, -1), (14, -1)], fill=EMP_CROWN)
    d.rectangle((10, 2, 21, 5), fill=EMP_FUR)
    d.ellipse((14, -3, 17, 0), fill=EMP_CROWN_JEWEL)
    
    # Eye
    d.rectangle((18, 9, 19, 11), fill=EYE)
    
    # Golden Sabre in right hand
    d.rectangle((24, 16, 26, 18), fill=SKIN)
    d.line([(25, 14), (25, 19)], fill=EMP_CROWN_JEWEL, width=1)
    d.rectangle((24, 4, 26, 13), fill=EMP_CROWN)
    d.point((25, 3), fill=EMP_CROWN)
    
    return img


def main() -> None:
    enemy_types = {
        "yuan_soldier": {
            "down": draw_soldier_down,
            "up": draw_soldier_up,
            "left": draw_soldier_left,
            "right": draw_soldier_right
        },
        "yuan_boss": {
            "down": draw_boss_down,
            "up": draw_boss_up,
            "left": draw_boss_left,
            "right": draw_boss_right
        },
        "yuan_emperor": {
            "down": draw_emperor_down,
            "up": draw_emperor_up,
            "left": draw_emperor_left,
            "right": draw_emperor_right
        }
    }
    
    for enemy_id, directions in enemy_types.items():
        enemy_dir = OUT / enemy_id
        enemy_dir.mkdir(parents=True, exist_ok=True)
        
        for name, func in directions.items():
            for frame in range(3):
                img = func(frame)
                path = enemy_dir / f"{name}_{frame}.png"
                img.save(path, "PNG")
                print(f"Generated enemy sprite: {path.relative_to(OUT.parent.parent)}")

if __name__ == "__main__":
    main()
