"""
Generate unique retro 8-bit sprites for NPCs in the Ming Dynasty RPG.
Each sprite is 32x32 pixels.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

TILE = 32
OUT = Path(__file__).resolve().parent.parent / "assets" / "npcs"
OUT.mkdir(parents=True, exist_ok=True)

# Common colors
SKIN = (255, 219, 172)
SKIN_SHADOW = (224, 172, 105)
SHOE = (40, 40, 40)
EYE = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (180, 180, 180)
BLACK = (0, 0, 0)

def create_base_sprite() -> Image.Image:
    return Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))

def draw_friend_xuda() -> Image.Image:
    """徐达: Young peasant boy with black hair topknot, wearing a blue tunic."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    d.rectangle((10, 29, 13, 31), fill=SHOE)
    d.rectangle((18, 29, 21, 31), fill=SHOE)
    
    # Blue Tunic
    d.rectangle((8, 14, 23, 28), fill=(33, 150, 243)) # Blue
    d.rectangle((8, 26, 23, 28), fill=(21, 101, 192)) # Dark Blue shadow
    d.rectangle((14, 14, 17, 28), fill=(100, 181, 246)) # Light Blue sash
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Black Hair & Topknot
    d.ellipse((13, 2, 18, 6), fill=BLACK) # Topknot
    d.arc((10, 5, 21, 15), 180, 360, fill=BLACK, width=2) # Hair outline
    
    # Eyes
    d.rectangle((12, 9, 13, 11), fill=EYE)
    d.rectangle((18, 9, 19, 11), fill=EYE)
    # Cheeks
    d.point((11, 11), fill=(255, 138, 128))
    d.point((20, 11), fill=(255, 138, 128))
    
    # Hands
    d.rectangle((6, 17, 9, 19), fill=SKIN)
    d.rectangle((22, 17, 25, 19), fill=SKIN)
    
    return img

def draw_elder_zhuwusi() -> Image.Image:
    """村长朱五四: Older peasant man with grey hair on sides, grey beard, wearing a brown robe."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    d.rectangle((10, 29, 13, 31), fill=SHOE)
    d.rectangle((18, 29, 21, 31), fill=SHOE)
    
    # Brown Robe
    d.rectangle((8, 14, 23, 28), fill=(121, 85, 72)) # Brown
    d.rectangle((8, 26, 23, 28), fill=(93, 64, 55)) # Dark Brown shadow
    d.rectangle((14, 14, 17, 28), fill=(161, 136, 127)) # Light sash
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Grey Hair & Beard
    d.arc((10, 5, 21, 15), 180, 360, fill=GREY, width=2) # Grey hair sides
    d.rectangle((12, 13, 19, 16), fill=GREY) # Beard
    d.point((11, 14), fill=GREY)
    d.point((20, 14), fill=GREY)
    
    # Eyes (looking tired/closed)
    d.line([(12, 10), (14, 10)], fill=EYE)
    d.line([(17, 10), (19, 10)], fill=EYE)
    
    # Hands
    d.rectangle((6, 17, 9, 19), fill=SKIN)
    d.rectangle((22, 17, 25, 19), fill=SKIN)
    
    return img

def draw_monk_abbot() -> Image.Image:
    """皇觉寺老和尚: Old bald monk with long white beard, wearing a saffron yellow robe."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    d.rectangle((10, 29, 13, 31), fill=SHOE)
    d.rectangle((18, 29, 21, 31), fill=SHOE)
    
    # Saffron Yellow Robe
    d.rectangle((8, 14, 23, 28), fill=(251, 192, 45)) # Yellow
    d.rectangle((8, 26, 23, 28), fill=(245, 124, 0)) # Orange shadow
    d.rectangle((14, 14, 17, 28), fill=(255, 235, 59)) # Light sash
    
    # Head (bald)
    d.ellipse((10, 4, 21, 15), fill=SKIN)
    d.arc((10, 4, 21, 15), 180, 360, fill=(240, 240, 240), width=1) # Bald head shine
    
    # Long White Beard
    d.polygon([(12, 13), (16, 19), (19, 13)], fill=WHITE) # Beard triangle
    d.rectangle((13, 13, 18, 15), fill=WHITE)
    
    # Eyes (kindly, closed curves)
    d.arc((11, 8, 14, 11), 0, 180, fill=EYE)
    d.arc((17, 8, 20, 11), 0, 180, fill=EYE)
    
    # Hands (holding Buddhist beads)
    d.rectangle((6, 17, 9, 19), fill=SKIN)
    d.rectangle((22, 17, 25, 19), fill=SKIN)
    # Beads
    d.point((13, 18), fill=(183, 28, 28))
    d.point((14, 19), fill=(183, 28, 28))
    d.point((15, 19), fill=(183, 28, 28))
    d.point((16, 18), fill=(183, 28, 28))
    
    return img

def draw_chang_yuchun() -> Image.Image:
    """常遇春: Strong young warrior with black hair, red headband, wearing a green tunic."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    d.rectangle((10, 29, 13, 31), fill=SHOE)
    d.rectangle((18, 29, 21, 31), fill=SHOE)
    
    # Green Tunic
    d.rectangle((7, 14, 24, 28), fill=(46, 125, 50)) # Green (wider for muscular build)
    d.rectangle((7, 26, 24, 28), fill=(27, 94, 32)) # Dark Green shadow
    d.rectangle((14, 14, 17, 28), fill=(229, 57, 53)) # Red warrior sash
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Red Headband & Black Hair
    d.rectangle((10, 6, 21, 8), fill=(229, 57, 53)) # Red headband
    d.arc((10, 5, 21, 15), 180, 360, fill=BLACK, width=1) # Hair
    
    # Fierce Eyes (angled eyebrows)
    d.line([(11, 8), (14, 10)], fill=BLACK, width=1) # Left eyebrow
    d.line([(20, 8), (17, 10)], fill=BLACK, width=1) # Right eyebrow
    d.rectangle((12, 10, 13, 11), fill=EYE)
    d.rectangle((18, 10, 19, 11), fill=EYE)
    
    # Hands
    d.rectangle((5, 17, 8, 19), fill=SKIN)
    d.rectangle((23, 17, 26, 19), fill=SKIN)
    
    return img

def draw_merchant() -> Image.Image:
    """行脚商人: Merchant wearing a blue headscarf, wearing a purple robe with a backpack."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    d.rectangle((10, 29, 13, 31), fill=SHOE)
    d.rectangle((18, 29, 21, 31), fill=SHOE)
    
    # Purple Robe
    d.rectangle((8, 14, 23, 28), fill=(103, 58, 183)) # Purple
    d.rectangle((8, 26, 23, 28), fill=(49, 27, 146)) # Dark Purple shadow
    d.rectangle((14, 14, 17, 28), fill=(255, 193, 7)) # Gold sash
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Blue Headscarf / Turban
    d.ellipse((11, 3, 20, 7), fill=(33, 150, 243)) # Turban top
    d.rectangle((10, 5, 21, 8), fill=(33, 150, 243)) # Turban band
    
    # Eyes & Mustache
    d.rectangle((12, 10, 13, 11), fill=EYE)
    d.rectangle((18, 10, 19, 11), fill=EYE)
    d.line([(11, 13), (20, 13)], fill=BLACK, width=1) # Mustache
    
    # Hands
    d.rectangle((6, 17, 9, 19), fill=SKIN)
    d.rectangle((22, 17, 25, 19), fill=SKIN)
    
    return img

def draw_farmer() -> Image.Image:
    """农夫阿福: Farmer wearing a straw hat, wearing a grey/brown tunic."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    
    # Feet
    d.rectangle((10, 29, 13, 31), fill=SHOE)
    d.rectangle((18, 29, 21, 31), fill=SHOE)
    
    # Grey/Brown Tunic
    d.rectangle((8, 14, 23, 28), fill=(158, 158, 158)) # Grey
    d.rectangle((8, 26, 23, 28), fill=(97, 97, 97)) # Dark Grey shadow
    d.rectangle((14, 14, 17, 28), fill=(121, 85, 72)) # Brown sash
    
    # Head
    d.ellipse((10, 5, 21, 15), fill=SKIN)
    
    # Yellow Straw Hat (wide brim)
    d.ellipse((6, 3, 25, 9), fill=(230, 180, 80)) # Hat brim
    d.ellipse((11, 1, 20, 5), fill=(255, 213, 79)) # Hat top
    
    # Eyes
    d.rectangle((12, 10, 13, 11), fill=EYE)
    d.rectangle((18, 10, 19, 11), fill=EYE)
    
    # Hands
    d.rectangle((6, 17, 9, 19), fill=SKIN)
    d.rectangle((22, 17, 25, 19), fill=SKIN)
    
    return img

def draw_wolf() -> Image.Image:
    """野狼: Grey wolf sprite with red eyes."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    # Body
    d.rectangle((6, 12, 26, 24), fill=(120, 120, 120)) # Grey body
    d.rectangle((8, 24, 11, 31), fill=(100, 100, 100)) # Legs
    d.rectangle((21, 24, 24, 31), fill=(100, 100, 100))
    # Head
    d.rectangle((22, 6, 30, 14), fill=(120, 120, 120))
    # Ears
    d.polygon([(23, 6), (25, 2), (27, 6)], fill=(100, 100, 100))
    # Red eyes
    d.point((27, 9), fill=(255, 0, 0))
    # Tail
    d.line([(6, 14), (2, 20)], fill=(100, 100, 100), width=3)
    return img

def draw_tiger() -> Image.Image:
    """猛虎: Orange tiger with black stripes."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    # Body
    d.rectangle((6, 10, 26, 24), fill=(245, 124, 0)) # Orange body
    # White belly
    d.rectangle((10, 20, 22, 24), fill=(255, 255, 255))
    # Legs
    d.rectangle((8, 24, 11, 31), fill=(230, 81, 0))
    d.rectangle((21, 24, 24, 31), fill=(230, 81, 0))
    # Stripes (black lines)
    d.line([(10, 10), (10, 16)], fill=(0, 0, 0), width=1)
    d.line([(15, 10), (15, 16)], fill=(0, 0, 0), width=1)
    d.line([(20, 10), (20, 16)], fill=(0, 0, 0), width=1)
    # Head
    d.rectangle((22, 6, 30, 15), fill=(245, 124, 0))
    # Eyes
    d.point((27, 9), fill=(0, 0, 0))
    # Tail
    d.line([(6, 12), (2, 8)], fill=(245, 124, 0), width=2)
    return img

def draw_lion() -> Image.Image:
    """狂狮: Yellow lion with brown mane."""
    img = create_base_sprite()
    d = ImageDraw.Draw(img)
    # Body
    d.rectangle((6, 12, 24, 24), fill=(251, 192, 45)) # Yellow body
    # Legs
    d.rectangle((8, 24, 11, 31), fill=(245, 124, 0))
    d.rectangle((19, 24, 22, 31), fill=(245, 124, 0))
    # Mane (brown circle/rect around head)
    d.rectangle((20, 4, 30, 16), fill=(141, 110, 99)) # Brown mane
    # Head
    d.rectangle((22, 7, 28, 14), fill=(251, 192, 45))
    # Eyes
    d.point((25, 9), fill=(0, 0, 0))
    # Tail
    d.line([(6, 14), (2, 22)], fill=(251, 192, 45), width=2)
    return img

def main() -> None:
    npcs = {
        "friend": draw_friend_xuda,
        "elder": draw_elder_zhuwusi,
        "monk": draw_monk_abbot,
        "chang": draw_chang_yuchun,
        "merchant": draw_merchant,
        "farmer": draw_farmer,
        "wolf": draw_wolf,
        "tiger": draw_tiger,
        "lion": draw_lion
    }
    
    for name, func in npcs.items():
        img = func()
        path = OUT / f"{name}.png"
        img.save(path, "PNG")
        print(f"Generated NPC sprite: {path.relative_to(OUT.parent.parent)}")

if __name__ == "__main__":
    main()
