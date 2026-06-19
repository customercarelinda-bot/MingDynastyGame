"""
Generate young Zhu Yuanzhang player sprites in 4 directions (down, up, left, right).
Each sprite is 32x32 pixels, using a retro 8-bit NES style.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

TILE = 32
OUT = Path(__file__).resolve().parent.parent / "assets" / "player"
OUT.mkdir(parents=True, exist_ok=True)

# Colors
SKIN = (255, 219, 172)
SKIN_SHADOW = (224, 172, 105)
ROBE = (188, 108, 37)       # Buddhist monk orange-brown robe
ROBE_DARK = (141, 73, 14)
ROBE_LIGHT = (221, 145, 72)
BOWL = (158, 158, 158)       # Grey metal/clay bowl
BOWL_INNER = (66, 66, 66)
BOWL_SHINE = (255, 255, 255)
HAIR_BALD = (240, 240, 240)  # Light grey shadow on bald head
SHOE = (40, 40, 40)
EYE = (0, 0, 0)

def create_base_sprite() -> Image.Image:
    return Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))

def draw_down(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet (walking animation)
    # frame 0: standing, frame 1: left foot up, frame 2: right foot up
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

    # Robe / Body
    d.rectangle((8, 14, 23, 28), fill=ROBE)
    d.rectangle((8, 26, 23, 28), fill=ROBE_DARK)  # Bottom shadow
    d.rectangle((14, 14, 17, 28), fill=ROBE_LIGHT) # Middle sash
    
    # Head (bald monk style)
    d.ellipse((10, 4, 21, 15), fill=SKIN)
    d.arc((10, 4, 21, 15), 180, 360, fill=HAIR_BALD, width=1) # Bald head outline/shading
    
    # Eyes
    d.rectangle((12, 9, 13, 11), fill=EYE)
    d.rectangle((18, 9, 19, 11), fill=EYE)
    # Cheeks
    d.point((11, 11), fill=(255, 138, 128))
    d.point((20, 11), fill=(255, 138, 128))
    
    # Hands & Bowl
    # Left hand
    d.rectangle((6, 17, 9, 19), fill=SKIN)
    # Right hand
    d.rectangle((22, 17, 25, 19), fill=SKIN)
    
    # The Bowl (朱元璋's famous bowl)
    # Held in front
    bowl_x, bowl_y = 12, 18
    d.ellipse((bowl_x, bowl_y, bowl_x + 7, bowl_y + 5), fill=BOWL)
    d.ellipse((bowl_x + 1, bowl_y, bowl_x + 6, bowl_y + 2), fill=BOWL_INNER)
    d.point((bowl_x + 2, bowl_y + 1), fill=BOWL_SHINE) # Shine
    
    return img

def draw_up(frame: int) -> Image.Image:
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

    # Robe / Body (back view)
    d.rectangle((8, 14, 23, 28), fill=ROBE)
    d.rectangle((8, 26, 23, 28), fill=ROBE_DARK)
    d.rectangle((11, 14, 20, 20), fill=ROBE_DARK) # Hood/collar shadow
    
    # Head (back of head, bald)
    d.ellipse((10, 4, 21, 15), fill=SKIN_SHADOW)
    d.ellipse((11, 5, 20, 14), fill=SKIN)
    
    return img

def draw_left(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((12, foot_y, 15, 31), fill=SHOE)
        d.rectangle((16, foot_y, 19, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((12, foot_y - 2, 15, 30), fill=SHOE)
        d.rectangle((16, foot_y, 19, 31), fill=SHOE)
    else:
        d.rectangle((12, foot_y, 15, 31), fill=SHOE)
        d.rectangle((16, foot_y - 2, 19, 30), fill=SHOE)

    # Robe / Body (profile)
    d.rectangle((10, 14, 21, 28), fill=ROBE)
    d.rectangle((10, 26, 21, 28), fill=ROBE_DARK)
    d.rectangle((9, 14, 11, 24), fill=ROBE_DARK) # Front shadow
    
    # Head (profile)
    d.ellipse((11, 4, 21, 15), fill=SKIN)
    d.arc((11, 4, 21, 15), 180, 360, fill=HAIR_BALD, width=1)
    
    # Eye (only one visible)
    d.rectangle((13, 9, 14, 11), fill=EYE)
    
    # Hand & Bowl (extended to the left)
    d.rectangle((7, 18, 11, 20), fill=SKIN)
    
    bowl_x, bowl_y = 4, 17
    d.ellipse((bowl_x, bowl_y, bowl_x + 6, bowl_y + 5), fill=BOWL)
    d.ellipse((bowl_x + 1, bowl_y, bowl_x + 5, bowl_y + 2), fill=BOWL_INNER)
    d.point((bowl_x + 2, bowl_y + 1), fill=BOWL_SHINE)
    
    return img

def draw_right(frame: int) -> Image.Image:
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    foot_y = 29
    if frame == 0:
        d.rectangle((12, foot_y, 15, 31), fill=SHOE)
        d.rectangle((16, foot_y, 19, 31), fill=SHOE)
    elif frame == 1:
        d.rectangle((12, foot_y - 2, 15, 30), fill=SHOE)
        d.rectangle((16, foot_y, 19, 31), fill=SHOE)
    else:
        d.rectangle((12, foot_y, 15, 31), fill=SHOE)
        d.rectangle((16, foot_y - 2, 19, 30), fill=SHOE)

    # Robe / Body (profile)
    d.rectangle((10, 14, 21, 28), fill=ROBE)
    d.rectangle((10, 26, 21, 28), fill=ROBE_DARK)
    d.rectangle((20, 14, 22, 24), fill=ROBE_DARK) # Front shadow
    
    # Head (profile)
    d.ellipse((10, 4, 20, 15), fill=SKIN)
    d.arc((10, 4, 20, 15), 180, 360, fill=HAIR_BALD, width=1)
    
    # Eye (only one visible)
    d.rectangle((17, 9, 18, 11), fill=EYE)
    
    # Hand & Bowl (extended to the right)
    d.rectangle((20, 18, 24, 20), fill=SKIN)
    
    bowl_x, bowl_y = 21, 17
    d.ellipse((bowl_x, bowl_y, bowl_x + 6, bowl_y + 5), fill=BOWL)
    d.ellipse((bowl_x + 1, bowl_y, bowl_x + 5, bowl_y + 2), fill=BOWL_INNER)
    d.point((bowl_x + 2, bowl_y + 1), fill=BOWL_SHINE)
    
    return img

def main() -> None:
    directions = {
        "down": draw_down,
        "up": draw_up,
        "left": draw_left,
        "right": draw_right
    }
    
    for name, func in directions.items():
        # Generate 3 frames: 0 (standing), 1 (left step), 2 (right step)
        for frame in range(3):
            img = func(frame)
            path = OUT / f"{name}_{frame}.png"
            img.save(path, "PNG")
            print(f"Generated player sprite: {path.relative_to(OUT.parent.parent)}")

if __name__ == "__main__":
    main()
