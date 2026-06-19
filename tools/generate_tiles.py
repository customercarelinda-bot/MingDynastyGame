"""
Generate NES-style 32x32 pixel map tiles for Ming Dynasty Game.
Run: python tools/generate_tiles.py
"""

from __future__ import annotations

import os
import random
from pathlib import Path

from PIL import Image, ImageDraw

TILE = 32
OUT = Path(__file__).resolve().parent.parent / "assets" / "tiles"

# NES-inspired palettes
PAL = {
    "grass1": (56, 142, 60),
    "grass2": (76, 175, 80),
    "grass3": (129, 199, 132),
    "grass_dark": (46, 125, 50),
    "dirt": (121, 85, 72),
    "dirt_light": (161, 136, 127),
    "stone": (158, 158, 158),
    "stone_dark": (97, 97, 97),
    "stone_light": (189, 189, 189),
    "asphalt": (66, 66, 66),
    "asphalt_light": (97, 97, 97),
    "water": (33, 150, 243),
    "water_dark": (21, 101, 192),
    "water_light": (100, 181, 246),
    "sand": (255, 213, 79),
    "sand_dark": (255, 183, 77),
    "snow": (236, 239, 241),
    "snow_shadow": (176, 190, 197),
    "rock": (109, 76, 65),
    "rock_light": (141, 110, 99),
    "rock_dark": (78, 52, 46),
    "wood": (121, 85, 72),
    "wood_dark": (93, 64, 55),
    "wood_light": (161, 136, 127),
    "thatch": (205, 164, 94),
    "leaf": (56, 142, 60),
    "leaf_dark": (27, 94, 32),
    "flower_red": (229, 57, 53),
    "flower_yellow": (253, 216, 53),
    "flower_pink": (236, 64, 122),
    "flower_white": (255, 255, 255),
    "wheat": (255, 235, 59),
    "wheat_dark": (251, 192, 45),
    "rice": (174, 213, 129),
    "crop_green": (102, 187, 106),
    "crop_dark": (67, 160, 71),
    "cactus": (76, 175, 80),
    "lava": (255, 87, 34),
    "magic": (171, 71, 188),
    "magic_light": (206, 147, 216),
    "fire": (255, 152, 0),
    "gold": (255, 193, 7),
    "brick": (183, 28, 28),
    "brick_dark": (136, 14, 79),
    "cave": (62, 39, 35),
    "cave_light": (93, 64, 55),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (120, 120, 120),
    "trap": (183, 28, 28),
    "metal": (96, 125, 139),
    "metal_light": (144, 164, 174),
}


def new_img(bg: tuple[int, int, int] = (0, 0, 0, 0)) -> Image.Image:
    return Image.new("RGBA", (TILE, TILE), bg)


def px(img: Image.Image, x: int, y: int, c: tuple) -> None:
    if 0 <= x < TILE and 0 <= y < TILE:
        img.putpixel((x, y), c)


def fill(img: Image.Image, c: tuple) -> None:
    ImageDraw.Draw(img).rectangle((0, 0, TILE - 1, TILE - 1), fill=c)


def rect(img: Image.Image, x0: int, y0: int, x1: int, y1: int, c: tuple) -> None:
    ImageDraw.Draw(img).rectangle((x0, y0, x1, y1), fill=c)


def noise_field(
    img: Image.Image,
    base: tuple,
    alt: tuple,
    density: float = 0.3,
    seed: int = 0,
) -> None:
    rng = random.Random(seed)
    fill(img, base)
    for y in range(TILE):
        for x in range(TILE):
            if rng.random() < density:
                px(img, x, y, alt)


def grass_base(img: Image.Image, seed: int = 0, dark: bool = False) -> None:
    base = PAL["grass_dark"] if dark else PAL["grass1"]
    alt = PAL["grass2"] if dark else PAL["grass3"]
    noise_field(img, base, alt, 0.35, seed)
    rng = random.Random(seed + 1)
    for _ in range(8):
        x, y = rng.randint(0, 31), rng.randint(0, 31)
        px(img, x, y, PAL["grass_dark"])


def draw_road_h(img: Image.Image, y0: int, y1: int, road: tuple, edge: tuple) -> None:
    fill(img, PAL["grass1"])
    rect(img, 0, y0, TILE - 1, y1, road)
    for x in range(0, TILE, 4):
        px(img, x, (y0 + y1) // 2, edge)


def draw_road_v(img: Image.Image, x0: int, x1: int, road: tuple, edge: tuple) -> None:
    fill(img, PAL["grass1"])
    rect(img, x0, 0, x1, TILE - 1, road)
    for y in range(0, TILE, 4):
        px(img, (x0 + x1) // 2, y, edge)


def stone_road_tile(variant: str) -> Image.Image:
    img = new_img()
    road, edge, crack = PAL["stone"], PAL["stone_dark"], PAL["dirt"]
    if variant == "直石子路":
        draw_road_h(img, 12, 19, road, edge)
        noise_field(img, PAL["grass1"], PAL["grass2"], 0.2, 1)
        for x in range(TILE):
            if not (12 <= 0):  # noqa: SIM114
                pass
        rect(img, 0, 0, TILE - 1, 11, PAL["grass1"])
        rect(img, 0, 20, TILE - 1, TILE - 1, PAL["grass1"])
    elif variant == "弯石子路":
        grass_base(img, 2)
        d = ImageDraw.Draw(img)
        d.ellipse((4, 4, 28, 28), fill=road)
        d.ellipse((8, 8, 24, 24), fill=PAL["grass1"])
        d.pieslice((4, 4, 28, 28), 200, 340, fill=road)
    elif variant == "石子路交叉口":
        fill(img, PAL["grass1"])
        rect(img, 0, 12, TILE - 1, 19, road)
        rect(img, 12, 0, 19, TILE - 1, road)
    elif variant == "带草缝的石子路":
        draw_road_h(img, 12, 19, road, edge)
        rng = random.Random(3)
        for x in range(TILE):
            if rng.random() < 0.4:
                px(img, x, 15, PAL["grass2"])
                px(img, x, 16, PAL["grass3"])
    elif variant == "破损石子路":
        draw_road_h(img, 12, 19, road, edge)
        for x, y in [(8, 14), (9, 15), (20, 17), (21, 16), (24, 13)]:
            px(img, x, y, crack)
            px(img, x + 1, y, crack)
    return img


def asphalt_tile(variant: str) -> Image.Image:
    img = new_img()
    road, line = PAL["asphalt"], PAL["white"]
    if variant == "直柏油路":
        fill(img, PAL["grass1"])
        rect(img, 0, 13, TILE - 1, 18, road)
        for x in range(2, TILE, 6):
            px(img, x, 15, line)
    elif variant == "弯柏油路":
        grass_base(img, 4)
        d = ImageDraw.Draw(img)
        d.pieslice((2, 2, 30, 30), 180, 270, fill=road)
        for i in range(4):
            px(img, 8 + i, 22 - i, line)
    elif variant == "道路交叉口":
        fill(img, PAL["grass1"])
        rect(img, 0, 13, TILE - 1, 18, road)
        rect(img, 13, 0, 18, TILE - 1, road)
    elif variant == "路边草地":
        fill(img, PAL["grass1"])
        rect(img, 0, 0, 18, TILE - 1, road)
        noise_field(img, PAL["grass1"], PAL["grass3"], 0.4, 5)
        rect(img, 19, 0, TILE - 1, TILE - 1, PAL["grass2"])
    elif variant == "带井盖的柏油路":
        fill(img, road)
        rect(img, 12, 12, 19, 19, PAL["metal"])
        for x in range(13, 19, 2):
            for y in range(13, 19, 2):
                px(img, x, y, PAL["metal_light"])
    return img


def mountain_tile(variant: str, alive: bool) -> Image.Image:
    img = new_img()
    if alive:
        base, rock_c, accent = PAL["grass1"], PAL["rock"], PAL["leaf"]
    else:
        base, rock_c, accent = PAL["dirt_light"], PAL["rock_dark"], PAL["rock"]

    if variant.endswith("绿色山坡") or variant == "有灌木的绿色山坡":
        grass_base(img, 10)
        d = ImageDraw.Draw(img)
        d.polygon([(0, 32), (16, 8), (32, 32)], fill=PAL["grass_dark"])
        d.polygon([(8, 32), (20, 14), (32, 32)], fill=PAL["grass2"])
        rect(img, 4, 20, 8, 24, accent)
        rect(img, 22, 18, 26, 22, accent)
    elif variant == "山路":
        grass_base(img, 11)
        d = ImageDraw.Draw(img)
        d.polygon([(0, 32), (16, 10), (32, 32)], fill=PAL["grass_dark"])
        rect(img, 10, 18, 22, 22, PAL["dirt"])
        for x in range(11, 22, 3):
            px(img, x, 20, PAL["stone_dark"])
    elif variant == "有藤蔓的山崖":
        grass_base(img, 12)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 16, 32, 32), fill=rock_c)
        for y in range(16, 32, 3):
            px(img, 5, y, PAL["leaf"])
            px(img, 6, y + 1, PAL["leaf_dark"])
            px(img, 20, y, PAL["leaf"])
    elif variant == "山洞入口":
        grass_base(img, 13)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 20, 32, 32), fill=rock_c)
        d.ellipse((10, 18, 22, 30), fill=PAL["cave"])
        d.ellipse((12, 20, 20, 28), fill=(20, 20, 30))
    elif variant == "有小瀑布的山":
        grass_base(img, 14)
        d = ImageDraw.Draw(img)
        d.polygon([(0, 32), (16, 6), (32, 32)], fill=PAL["grass_dark"])
        for y in range(10, 28):
            px(img, 16, y, PAL["water_light"])
            if y % 2 == 0:
                px(img, 17, y, PAL["water"])
    elif variant == "光秃的岩石山坡":
        noise_field(img, PAL["dirt_light"], PAL["rock_light"], 0.4, 20)
        d = ImageDraw.Draw(img)
        d.polygon([(0, 32), (16, 10), (32, 32)], fill=rock_c)
    elif variant == "碎石山顶":
        noise_field(img, rock_c, PAL["stone"], 0.5, 21)
        d = ImageDraw.Draw(img)
        d.polygon([(4, 32), (16, 4), (28, 32)], fill=PAL["stone_dark"])
    elif variant == "干裂的岩石表面":
        fill(img, rock_c)
        d = ImageDraw.Draw(img)
        for i in range(0, 32, 6):
            d.line([(i, 0), (i + 8, 32)], fill=PAL["rock_dark"], width=1)
        for i in range(0, 32, 8):
            d.line([(0, i), (32, i + 4)], fill=PAL["rock_dark"], width=1)
    elif variant == "长有枯枝的山":
        fill(img, PAL["dirt"])
        d = ImageDraw.Draw(img)
        d.polygon([(0, 32), (16, 12), (32, 32)], fill=rock_c)
        d.line([(10, 20), (10, 8)], fill=PAL["wood_dark"], width=2)
        d.line([(10, 12), (6, 10)], fill=PAL["wood_dark"], width=1)
        d.line([(10, 16), (14, 14)], fill=PAL["wood_dark"], width=1)
    elif variant == "荒芜的悬崖边":
        fill(img, PAL["dirt_light"])
        rect(img, 0, 20, 32, 32, rock_c)
        for x in range(0, 32, 2):
            px(img, x, 19, PAL["rock_dark"])
    return img


def forest_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "密集树群（俯视）":
        fill(img, PAL["grass_dark"])
        for cx, cy in [(8, 8), (24, 8), (8, 24), (24, 24), (16, 16)]:
            d = ImageDraw.Draw(img)
            d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=PAL["leaf_dark"])
            d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=PAL["leaf"])
    elif variant == "稀疏树群":
        grass_base(img, 30)
        for cx, cy in [(10, 12), (24, 22)]:
            ImageDraw.Draw(img).ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=PAL["leaf"])
            px(img, cx, cy + 4, PAL["wood_dark"])
    elif variant == "草地上的树影":
        grass_base(img, 31)
        d = ImageDraw.Draw(img)
        d.ellipse((10, 14, 22, 22), fill=(30, 50, 30, 180))
    elif variant == "森林小径":
        grass_base(img, 32)
        rect(img, 13, 0, 18, 31, PAL["dirt"])
        for y in range(0, 32, 5):
            px(img, 15, y, PAL["dirt_light"])
    elif variant == "长有小蘑菇的森林":
        grass_base(img, 33)
        for cx, cy, col in [(8, 20, PAL["flower_red"]), (22, 14, PAL["flower_white"]), (18, 26, PAL["flower_red"])]:
            px(img, cx, cy, col)
            px(img, cx, cy + 1, PAL["flower_white"])
            px(img, cx - 1, cy + 2, PAL["flower_white"])
            px(img, cx + 1, cy + 2, PAL["flower_white"])
    return img


def village_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "茅草屋顶":
        fill(img, PAL["thatch"])
        d = ImageDraw.Draw(img)
        for x in range(0, 32, 4):
            d.line([(x, 0), (x + 8, 32)], fill=PAL["wood_dark"], width=1)
        rect(img, 0, 24, 31, 31, PAL["wood"])
    elif variant == "木墙":
        fill(img, PAL["wood"])
        for y in range(0, 32, 4):
            rect(img, 0, y, 31, y + 1, PAL["wood_dark"])
        for x in range(0, 32, 8):
            rect(img, x, 0, x + 1, 31, PAL["wood_dark"])
    elif variant == "村庄围栏":
        grass_base(img, 40)
        for x in range(2, 30, 6):
            rect(img, x, 8, x + 2, 28, PAL["wood"])
            rect(img, x - 1, 12, x + 3, 14, PAL["wood_dark"])
    elif variant == "木门":
        fill(img, PAL["wood_dark"])
        rect(img, 8, 4, 23, 31, PAL["wood"])
        rect(img, 14, 16, 17, 19, PAL["gold"])
    elif variant == "村庄水井":
        grass_base(img, 41)
        d = ImageDraw.Draw(img)
        d.ellipse((8, 8, 24, 24), fill=PAL["stone"])
        d.ellipse((11, 11, 21, 21), fill=PAL["water_dark"])
        rect(img, 14, 4, 18, 10, PAL["wood"])
    return img


def water_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "平静的河面":
        noise_field(img, PAL["water"], PAL["water_light"], 0.25, 50)
    elif variant == "有波纹的流动河水":
        fill(img, PAL["water"])
        d = ImageDraw.Draw(img)
        for y in range(4, 32, 6):
            d.arc((-4, y - 2, 36, y + 4), 0, 180, fill=PAL["water_light"])
    elif variant == "有鹅卵石的浅水":
        fill(img, PAL["water_light"])
        rng = random.Random(51)
        for _ in range(20):
            x, y = rng.randint(0, 31), rng.randint(0, 31)
            c = PAL["stone"] if rng.random() < 0.5 else PAL["stone_light"]
            px(img, x, y, c)
    elif variant == "小池塘":
        grass_base(img, 52)
        d = ImageDraw.Draw(img)
        d.ellipse((6, 6, 26, 26), fill=PAL["water"])
        d.ellipse((10, 10, 22, 22), fill=PAL["water_light"])
    elif variant == "长有芦苇的水边":
        fill(img, PAL["water"])
        rect(img, 0, 0, 31, 10, PAL["grass2"])
        for x in range(4, 28, 5):
            for y in range(2, 10):
                px(img, x, y, PAL["grass_dark"])
            px(img, x + 1, 8, PAL["thatch"])
    elif variant == "深水":
        fill(img, PAL["water_dark"])
        rng = random.Random(54)
        for _ in range(15):
            px(img, rng.randint(0, 31), rng.randint(0, 31), PAL["water"])
    return img


def transition_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "草地与山的过渡":
        grass_base(img, 60)
        d = ImageDraw.Draw(img)
        d.polygon([(0, 32), (32, 0), (32, 32)], fill=PAL["grass_dark"])
        d.polygon([(16, 32), (32, 8), (32, 32)], fill=PAL["rock"])
    elif variant == "草地与水的过渡":
        grass_base(img, 61)
        d = ImageDraw.Draw(img)
        d.rectangle((16, 0, 32, 32), fill=PAL["water"])
        for y in range(0, 32, 3):
            px(img, 15, y, PAL["grass3"])
    elif variant == "路与森林的过渡":
        rect(img, 0, 0, 15, 31, PAL["dirt"])
        grass_base(img, 62)
        d = ImageDraw.Draw(img)
        d.rectangle((16, 0, 32, 32), fill=PAL["grass_dark"])
        d.ellipse((22, 10, 30, 18), fill=PAL["leaf_dark"])
    elif variant == "荒山与草地的过渡":
        noise_field(img, PAL["dirt_light"], PAL["rock"], 0.3, 63)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, 14, 32), fill=PAL["grass1"])
        for y in range(32):
            px(img, 14, y, PAL["grass_dark"])
    elif variant == "村庄与路的过渡":
        rect(img, 0, 0, 14, 31, PAL["dirt"])
        rect(img, 15, 0, 31, 31, PAL["wood"])
        rect(img, 15, 0, 31, 8, PAL["thatch"])
    return img


def prop_tile(variant: str) -> Image.Image:
    img = new_img()
    grass_base(img, 70)
    if variant == "木制路标":
        rect(img, 14, 10, 17, 28, PAL["wood"])
        rect(img, 8, 10, 23, 16, PAL["wood_light"])
        px(img, 10, 12, PAL["dirt"])
        px(img, 18, 12, PAL["dirt"])
    elif variant == "小石碑":
        rect(img, 12, 14, 19, 28, PAL["stone"])
        rect(img, 13, 10, 18, 15, PAL["stone_light"])
    elif variant == "篝火":
        rect(img, 13, 20, 18, 24, PAL["wood_dark"])
        d = ImageDraw.Draw(img)
        d.ellipse((10, 10, 22, 22), fill=PAL["fire"])
        d.ellipse((13, 13, 19, 19), fill=PAL["flower_yellow"])
    elif variant == "木桶":
        d = ImageDraw.Draw(img)
        d.ellipse((10, 16, 22, 28), fill=PAL["wood"])
        rect(img, 10, 12, 22, 20, PAL["wood_light"])
        rect(img, 10, 12, 22, 14, PAL["wood_dark"])
    elif variant == "破损的木车":
        rect(img, 6, 18, 26, 24, PAL["wood"])
        for x in range(8, 24, 8):
            d = ImageDraw.Draw(img)
            d.ellipse((x, 22, x + 6, 28), fill=PAL["wood_dark"])
        px(img, 20, 14, PAL["wood_light"])
        px(img, 22, 16, PAL["wood"])
    return img


def farm_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "整齐的麦田":
        fill(img, PAL["wheat"])
        for x in range(0, 32, 4):
            for y in range(0, 32, 4):
                px(img, x, y, PAL["wheat_dark"])
                px(img, x, y + 1, PAL["thatch"])
    elif variant == "稻田":
        fill(img, PAL["water_light"])
        for x in range(0, 32, 4):
            for y in range(0, 32, 4):
                px(img, x, y, PAL["rice"])
                px(img, x + 1, y, PAL["crop_green"])
    elif variant == "菜地":
        fill(img, PAL["dirt"])
        for x in range(2, 30, 6):
            for y in range(2, 30, 6):
                rect(img, x, y, x + 3, y + 3, PAL["crop_green"])
    elif variant == "农田小路":
        fill(img, PAL["crop_green"])
        rect(img, 13, 0, 18, 31, PAL["dirt"])
    elif variant == "农田边缘的篱笆":
        fill(img, PAL["crop_green"])
        for x in range(0, 32, 4):
            rect(img, x, 0, x + 1, 31, PAL["wood"])
            rect(img, x, 0, x + 2, 2, PAL["wood_dark"])
    return img


def flower_tile(variant: str) -> Image.Image:
    img = new_img()
    grass_base(img, 80)
    colors = [PAL["flower_red"], PAL["flower_yellow"], PAL["flower_pink"], PAL["flower_white"]]
    if variant == "大片花丛":
        for y in range(0, 32, 3):
            for x in range(0, 32, 3):
                px(img, x, y, colors[(x + y) % 4])
    elif variant == "野花丛":
        rng = random.Random(81)
        for _ in range(40):
            px(img, rng.randint(0, 31), rng.randint(0, 31), rng.choice(colors))
    elif variant == "带蝴蝶的花丛":
        for _ in range(30):
            px(img, random.randint(0, 31), random.randint(0, 31), random.choice(colors))
        d = ImageDraw.Draw(img)
        d.ellipse((14, 10, 18, 14), fill=PAL["flower_yellow"])
        d.ellipse((18, 10, 22, 14), fill=PAL["flower_white"])
        px(img, 16, 12, PAL["black"])
    elif variant == "花丛小径":
        for y in range(0, 32, 3):
            for x in range(0, 32, 3):
                if not (12 <= x <= 19):
                    px(img, x, y, colors[(x + y) % 4])
        rect(img, 13, 0, 18, 31, PAL["dirt_light"])
    elif variant == "花丛中的石头":
        for _ in range(25):
            px(img, random.randint(0, 31), random.randint(0, 31), random.choice(colors))
        rect(img, 12, 14, 20, 22, PAL["stone"])
    return img


def desert_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "沙地":
        noise_field(img, PAL["sand"], PAL["sand_dark"], 0.35, 90)
    elif variant == "沙丘":
        fill(img, PAL["sand"])
        d = ImageDraw.Draw(img)
        d.arc((-8, 10, 40, 34), 180, 360, fill=PAL["sand_dark"])
    elif variant == "带仙人掌的沙地":
        noise_field(img, PAL["sand"], PAL["sand_dark"], 0.3, 91)
        rect(img, 14, 12, 17, 28, PAL["cactus"])
        rect(img, 10, 16, 13, 18, PAL["cactus"])
        rect(img, 18, 18, 21, 20, PAL["cactus"])
    elif variant == "沙漠岩石":
        noise_field(img, PAL["sand"], PAL["sand_dark"], 0.2, 92)
        rect(img, 8, 14, 24, 26, PAL["rock"])
        rect(img, 10, 12, 14, 16, PAL["rock_light"])
    elif variant == "沙漠中的枯树":
        noise_field(img, PAL["sand"], PAL["sand_dark"], 0.25, 93)
        d = ImageDraw.Draw(img)
        d.line([(16, 28), (16, 10)], fill=PAL["wood_dark"], width=2)
        d.line([(16, 14), (10, 10)], fill=PAL["wood_dark"], width=1)
        d.line([(16, 18), (22, 14)], fill=PAL["wood_dark"], width=1)
    return img


def snow_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "积雪覆盖的地面":
        noise_field(img, PAL["snow"], PAL["snow_shadow"], 0.2, 100)
    elif variant == "雪坡":
        fill(img, PAL["snow"])
        d = ImageDraw.Draw(img)
        d.polygon([(0, 32), (16, 8), (32, 32)], fill=PAL["snow_shadow"])
    elif variant == "雪地小径":
        noise_field(img, PAL["snow"], PAL["snow_shadow"], 0.15, 101)
        rect(img, 12, 0, 19, 31, PAL["dirt_light"])
    elif variant == "雪堆":
        noise_field(img, PAL["snow"], PAL["snow_shadow"], 0.15, 102)
        d = ImageDraw.Draw(img)
        d.ellipse((8, 16, 24, 28), fill=PAL["white"])
        d.ellipse((10, 14, 22, 24), fill=PAL["snow"])
    elif variant == "雪中的岩石":
        noise_field(img, PAL["snow"], PAL["snow_shadow"], 0.2, 103)
        rect(img, 10, 14, 22, 24, PAL["stone"])
    return img


def beach_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "沙滩":
        noise_field(img, PAL["sand"], PAL["sand_dark"], 0.3, 110)
    elif variant == "沙滩上的贝壳":
        noise_field(img, PAL["sand"], PAL["sand_dark"], 0.25, 111)
        for x, y in [(8, 12), (20, 20), (14, 26)]:
            px(img, x, y, PAL["flower_white"])
            px(img, x + 1, y, PAL["flower_pink"])
    elif variant == "海边岩石":
        fill(img, PAL["water_light"])
        rect(img, 0, 0, 31, 12, PAL["sand"])
        rect(img, 8, 10, 24, 28, PAL["rock"])
    elif variant == "海水浪花":
        fill(img, PAL["water"])
        for x in range(0, 32, 2):
            px(img, x, 8, PAL["white"])
            px(img, x + 1, 10, PAL["water_light"])
        rect(img, 0, 12, 31, 31, PAL["sand"])
    elif variant == "沙滩上的椰子树":
        noise_field(img, PAL["sand"], PAL["sand_dark"], 0.2, 112)
        d = ImageDraw.Draw(img)
        d.line([(16, 28), (16, 12)], fill=PAL["wood_dark"], width=2)
        d.ellipse((10, 4, 22, 14), fill=PAL["leaf"])
    return img


def castle_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "城堡城墙":
        fill(img, PAL["stone"])
        for y in range(0, 32, 8):
            for x in range(0, 32, 8):
                rect(img, x, y, x + 5, y + 5, PAL["stone_light"])
        rect(img, 0, 24, 31, 31, PAL["stone_dark"])
    elif variant == "城堡塔楼":
        fill(img, PAL["stone_dark"])
        rect(img, 8, 4, 23, 31, PAL["stone"])
        for y in range(4, 10, 3):
            rect(img, 6, y, 25, y + 1, PAL["stone_light"])
        rect(img, 12, 0, 19, 6, PAL["brick"])
    elif variant == "城堡大门":
        fill(img, PAL["stone"])
        rect(img, 4, 0, 27, 31, PAL["stone_dark"])
        d = ImageDraw.Draw(img)
        d.ellipse((10, 14, 22, 32), fill=PAL["wood_dark"])
        rect(img, 10, 14, 22, 28, PAL["wood"])
    elif variant == "城堡内的石板路":
        fill(img, PAL["stone_dark"])
        for y in range(0, 32, 8):
            for x in range(0, 32, 8):
                rect(img, x, y, x + 6, y + 6, PAL["stone"])
    elif variant == "城堡花园":
        grass_base(img, 120)
        for x, y in [(8, 8), (24, 10), (12, 22), (22, 24)]:
            px(img, x, y, PAL["flower_red"])
            px(img, x + 1, y, PAL["flower_yellow"])
        rect(img, 14, 14, 18, 18, PAL["stone_light"])
    return img


def town_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "石板街道":
        fill(img, PAL["stone"])
        for y in range(0, 32, 8):
            for x in range(0, 32, 8):
                px(img, x, y, PAL["stone_dark"])
    elif variant == "街道旁的房屋":
        rect(img, 0, 0, 14, 31, PAL["stone"])
        rect(img, 0, 0, 14, 10, PAL["brick"])
        rect(img, 16, 0, 31, 31, PAL["stone_dark"])
    elif variant == "路灯":
        grass_base(img, 121)
        rect(img, 15, 8, 16, 28, PAL["metal"])
        d = ImageDraw.Draw(img)
        d.ellipse((11, 4, 20, 12), fill=PAL["flower_yellow"])
    elif variant == "街道上的摊位":
        rect(img, 0, 20, 31, 31, PAL["stone_dark"])
        rect(img, 4, 10, 28, 20, PAL["thatch"])
        rect(img, 6, 14, 12, 18, PAL["wood"])
        rect(img, 18, 14, 26, 18, PAL["wood"])
    elif variant == "下水道入口":
        fill(img, PAL["stone_dark"])
        rect(img, 10, 10, 21, 21, PAL["metal"])
        for x in range(12, 20, 2):
            rect(img, x, 12, x, 18, PAL["black"])
    return img


def ruin_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "破损的墙壁":
        fill(img, PAL["dirt"])
        rect(img, 0, 0, 31, 20, PAL["brick"])
        for x, y in [(5, 8), (12, 4), (20, 10), (8, 14)]:
            px(img, x, y, PAL["dirt"])
            px(img, x + 1, y, PAL["grass1"])
    elif variant == "倒塌的石柱":
        grass_base(img, 130)
        rect(img, 12, 0, 19, 18, PAL["stone"])
        rect(img, 8, 18, 24, 22, PAL["stone_dark"])
        for x in range(8, 24):
            px(img, x, 20, PAL["stone"])
    elif variant == "废墟中的砖块":
        fill(img, PAL["dirt"])
        rng = random.Random(131)
        for _ in range(25):
            x, y = rng.randint(0, 28), rng.randint(0, 28)
            rect(img, x, y, x + 3, y + 2, PAL["brick"])
    elif variant == "废弃的建筑地基":
        grass_base(img, 132)
        rect(img, 4, 16, 27, 27, PAL["stone_dark"])
        for x in range(6, 26, 5):
            rect(img, x, 16, x + 2, 22, PAL["stone"])
    elif variant == "废墟中的宝箱":
        grass_base(img, 133)
        rect(img, 10, 14, 22, 24, PAL["wood_dark"])
        rect(img, 10, 12, 22, 16, PAL["wood"])
        rect(img, 14, 16, 18, 18, PAL["gold"])
    return img


def cave_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "洞穴石壁":
        noise_field(img, PAL["cave"], PAL["cave_light"], 0.4, 140)
    elif variant == "洞穴地面的碎石":
        fill(img, PAL["cave"])
        rng = random.Random(141)
        for _ in range(35):
            px(img, rng.randint(0, 31), rng.randint(0, 31), rng.choice([PAL["stone_dark"], PAL["rock"], PAL["gray"]]))
    elif variant == "洞穴中的火把":
        fill(img, PAL["cave"])
        rect(img, 14, 12, 17, 24, PAL["wood"])
        d = ImageDraw.Draw(img)
        d.ellipse((12, 6, 20, 14), fill=PAL["fire"])
    elif variant == "洞穴岔路":
        fill(img, PAL["cave"])
        rect(img, 0, 13, 31, 18, PAL["cave_light"])
        rect(img, 13, 0, 18, 13, PAL["cave_light"])
    elif variant == "洞穴中的水池":
        noise_field(img, PAL["cave"], PAL["cave_light"], 0.3, 142)
        d = ImageDraw.Draw(img)
        d.ellipse((6, 14, 26, 28), fill=PAL["water_dark"])
    return img


def magic_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "魔法阵":
        fill(img, PAL["cave"])
        d = ImageDraw.Draw(img)
        d.ellipse((4, 4, 28, 28), outline=PAL["magic"], width=2)
        d.ellipse((10, 10, 22, 22), outline=PAL["magic_light"], width=1)
        px(img, 16, 8, PAL["magic_light"])
        px(img, 16, 24, PAL["magic_light"])
    elif variant == "发光的水晶":
        grass_base(img, 150)
        d = ImageDraw.Draw(img)
        d.polygon([(16, 6), (22, 20), (10, 20)], fill=PAL["magic"])
        d.polygon([(16, 10), (19, 18), (13, 18)], fill=PAL["magic_light"])
    elif variant == "漂浮的魔法符文":
        fill(img, PAL["cave"])
        for x, y in [(10, 10), (22, 10), (16, 22)]:
            px(img, x, y, PAL["magic_light"])
            px(img, x + 1, y, PAL["magic"])
            px(img, x, y + 1, PAL["magic"])
    elif variant == "魔法火焰":
        fill(img, PAL["cave"])
        d = ImageDraw.Draw(img)
        d.ellipse((10, 8, 22, 24), fill=PAL["magic"])
        d.ellipse((13, 12, 19, 20), fill=PAL["magic_light"])
    elif variant == "魔法迷雾":
        fill(img, PAL["cave"])
        d = ImageDraw.Draw(img)
        for i in range(5):
            d.ellipse((i * 4, 8 + i * 2, i * 4 + 20, 24 + i * 2), fill=(171, 71, 188, 80))
    return img


def trap_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "地板尖刺":
        fill(img, PAL["stone_dark"])
        for x in range(4, 28, 4):
            for y in range(4, 28, 4):
                d = ImageDraw.Draw(img)
                d.polygon([(x, y + 3), (x + 1, y), (x + 2, y + 3)], fill=PAL["metal"])
    elif variant == "压力板":
        fill(img, PAL["stone"])
        rect(img, 8, 14, 23, 22, PAL["metal"])
        rect(img, 10, 16, 21, 20, PAL["metal_light"])
    elif variant == "易碎的地砖":
        fill(img, PAL["stone"])
        d = ImageDraw.Draw(img)
        for x in range(0, 32, 8):
            for y in range(0, 32, 8):
                d.line([(x, y), (x + 7, y + 7)], fill=PAL["stone_dark"])
    elif variant == "陷阱门":
        fill(img, PAL["wood_dark"])
        rect(img, 6, 6, 25, 25, PAL["wood"])
        rect(img, 14, 6, 17, 25, PAL["black"])
    elif variant == "隐藏的暗箭":
        fill(img, PAL["stone_dark"])
        rect(img, 0, 14, 10, 17, PAL["black"])
        for x in range(12, 28):
            px(img, x, 15, PAL["wood"])
            px(img, x, 16, PAL["wood_light"])
    return img


def mechanism_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "杠杆":
        fill(img, PAL["stone_dark"])
        rect(img, 14, 18, 17, 28, PAL["wood_dark"])
        rect(img, 6, 14, 25, 17, PAL["wood"])
        rect(img, 14, 12, 17, 15, PAL["metal"])
    elif variant == "开关":
        fill(img, PAL["cave"])
        rect(img, 10, 14, 21, 24, PAL["metal"])
        rect(img, 14, 10, 17, 16, PAL["fire"])
    elif variant == "魔法封印":
        fill(img, PAL["stone_dark"])
        d = ImageDraw.Draw(img)
        d.rectangle((8, 8, 24, 24), outline=PAL["magic"], width=2)
        d.line([(8, 8), (24, 24)], fill=PAL["magic_light"])
        d.line([(24, 8), (8, 24)], fill=PAL["magic_light"])
    elif variant == "转动的齿轮":
        fill(img, PAL["stone_dark"])
        d = ImageDraw.Draw(img)
        d.ellipse((8, 8, 24, 24), fill=PAL["metal"])
        d.ellipse((12, 12, 20, 20), fill=PAL["stone_dark"])
        for i in range(8):
            px(img, 16 + int(8 * __import__("math").cos(i * 0.785)), 16 + int(8 * __import__("math").sin(i * 0.785)), PAL["metal_light"])
    elif variant == "升降平台":
        fill(img, PAL["cave"])
        rect(img, 4, 16, 27, 26, PAL["metal"])
        for x in range(6, 26, 4):
            rect(img, x, 16, x + 1, 26, PAL["metal_light"])
        rect(img, 14, 8, 17, 16, PAL["stone"])
    return img


def monster_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "怪物巢穴入口":
        fill(img, PAL["dirt"])
        d = ImageDraw.Draw(img)
        d.ellipse((8, 12, 24, 28), fill=PAL["cave"])
        for x in range(10, 22):
            px(img, x, 12, PAL["rock_dark"])
        rect(img, 12, 6, 20, 12, PAL["white"])
    elif variant == "怪物脚印":
        fill(img, PAL["dirt"])
        d = ImageDraw.Draw(img)
        for ox in [8, 20]:
            d.ellipse((ox, 10, ox + 6, 18), fill=PAL["dirt_light"])
            d.ellipse((ox + 2, 18, ox + 4, 22), fill=PAL["dirt_light"])
    elif variant == "怪物的骨头堆":
        fill(img, PAL["cave"])
        for x, y in [(10, 18), (16, 20), (20, 16), (14, 14)]:
            rect(img, x, y, x + 4, y + 2, PAL["white"])
        px(img, 12, 16, PAL["white"])
        px(img, 18, 18, PAL["white"])
    elif variant == "怪物的粪便":
        grass_base(img, 160)
        d = ImageDraw.Draw(img)
        d.ellipse((10, 16, 18, 24), fill=(93, 64, 55))
        d.ellipse((18, 18, 24, 26), fill=(78, 52, 46))
    elif variant == "怪物的爪痕":
        fill(img, PAL["rock"])
        d = ImageDraw.Draw(img)
        for i in range(3):
            d.line([(10 + i * 4, 8), (6 + i * 4, 24)], fill=PAL["rock_dark"], width=2)
    return img


def tree_tile(variant: str) -> Image.Image:
    img = new_img()
    grass_base(img, 170)
    if variant == "橡树":
        d = ImageDraw.Draw(img)
        d.ellipse((6, 4, 26, 22), fill=PAL["leaf_dark"])
        d.ellipse((10, 8, 22, 20), fill=PAL["leaf"])
        rect(img, 14, 18, 17, 28, PAL["wood_dark"])
    elif variant == "松树":
        d = ImageDraw.Draw(img)
        d.polygon([(16, 4), (6, 18), (26, 18)], fill=PAL["leaf_dark"])
        d.polygon([(16, 10), (9, 22), (23, 22)], fill=PAL["leaf"])
        rect(img, 14, 20, 17, 28, PAL["wood_dark"])
    elif variant == "枫树":
        d = ImageDraw.Draw(img)
        d.ellipse((6, 6, 26, 20), fill=(198, 40, 40))
        d.ellipse((10, 10, 22, 18), fill=(255, 112, 67))
        rect(img, 14, 16, 17, 28, PAL["wood_dark"])
    elif variant == "枯树":
        d = ImageDraw.Draw(img)
        d.line([(16, 28), (16, 8)], fill=PAL["wood_dark"], width=2)
        d.line([(16, 14), (8, 8)], fill=PAL["wood_dark"], width=1)
        d.line([(16, 18), (24, 12)], fill=PAL["wood_dark"], width=1)
    elif variant == "被砍伐的树桩":
        d = ImageDraw.Draw(img)
        d.ellipse((10, 18, 22, 28), fill=PAL["wood"])
        d.ellipse((11, 19, 21, 25), fill=PAL["wood_light"])
        for x in range(12, 21, 3):
            px(img, x, 20, PAL["wood_dark"])
    elif variant == "树上的鸟巢":
        d = ImageDraw.Draw(img)
        d.ellipse((8, 8, 24, 22), fill=PAL["leaf"])
        rect(img, 14, 16, 17, 26, PAL["wood_dark"])
        d.ellipse((16, 12, 24, 18), fill=PAL["thatch"])
    elif variant == "树藤缠绕的树":
        d = ImageDraw.Draw(img)
        d.ellipse((8, 6, 24, 20), fill=PAL["leaf_dark"])
        rect(img, 14, 16, 17, 28, PAL["wood_dark"])
        for y in range(8, 24):
            px(img, 10 + (y % 3), y, PAL["leaf"])
            px(img, 20 - (y % 3), y, PAL["leaf_dark"])
    return img


def furniture_tile(variant: str) -> Image.Image:
    img = new_img()
    fill(img, PAL["wood_dark"])
    if variant == "桌子":
        rect(img, 4, 14, 27, 22, PAL["wood"])
        rect(img, 6, 22, 9, 30, PAL["wood_dark"])
        rect(img, 22, 22, 25, 30, PAL["wood_dark"])
    elif variant == "椅子":
        rect(img, 10, 16, 21, 22, PAL["wood"])
        rect(img, 10, 10, 21, 16, PAL["wood_light"])
        rect(img, 10, 22, 13, 30, PAL["wood_dark"])
        rect(img, 18, 22, 21, 30, PAL["wood_dark"])
    elif variant == "床":
        rect(img, 4, 14, 27, 28, PAL["wood"])
        rect(img, 4, 10, 27, 16, PAL["brick_dark"])
        rect(img, 6, 16, 25, 26, PAL["flower_white"])
    elif variant == "书架":
        rect(img, 6, 4, 25, 30, PAL["wood"])
        for y in range(8, 28, 8):
            rect(img, 6, y, 25, y + 2, PAL["wood_dark"])
        for y in range(6, 26, 10):
            px(img, 10, y, PAL["flower_red"])
            px(img, 18, y + 2, PAL["flower_yellow"])
    elif variant == "壁炉":
        rect(img, 0, 0, 31, 31, PAL["stone_dark"])
        rect(img, 8, 8, 23, 28, PAL["brick"])
        d = ImageDraw.Draw(img)
        d.ellipse((10, 16, 21, 28), fill=PAL["black"])
        d.ellipse((12, 14, 19, 22), fill=PAL["fire"])
    return img


def grass_tile(variant: str) -> Image.Image:
    img = new_img()
    if variant == "普通草地":
        grass_base(img, 0)
    elif variant == "带小花的草地":
        grass_base(img, 1)
        for x, y, c in [(6, 8, PAL["flower_yellow"]), (20, 14, PAL["flower_white"]), (12, 22, PAL["flower_pink"]), (26, 6, PAL["flower_red"])]:
            px(img, x, y, c)
            px(img, x, y + 1, PAL["grass_dark"])
    elif variant == "干草":
        noise_field(img, (189, 154, 76), (205, 164, 94), 0.4, 2)
    elif variant == "带石块的草地":
        grass_base(img, 3)
        for x, y in [(8, 10), (9, 11), (20, 18), (21, 17), (14, 24)]:
            px(img, x, y, PAL["stone"])
    elif variant == "草地小径边缘":
        grass_base(img, 4)
        rect(img, 0, 14, 14, 17, PAL["dirt"])
        for x in range(14, 32):
            px(img, x, 15, PAL["grass3"])
            px(img, x, 16, PAL["grass2"])
    return img


# Category registry: folder_name -> list of (filename, generator_callable)
CATEGORIES: dict[str, list[tuple[str, callable]]] = {
    "01_草地": [(n, lambda n=n: grass_tile(n)) for n in [
        "普通草地", "带小花的草地", "干草", "带石块的草地", "草地小径边缘",
    ]],
    "02_石子路": [(n, lambda n=n: stone_road_tile(n)) for n in [
        "直石子路", "弯石子路", "石子路交叉口", "带草缝的石子路", "破损石子路",
    ]],
    "03_柏油路": [(n, lambda n=n: asphalt_tile(n)) for n in [
        "直柏油路", "弯柏油路", "道路交叉口", "路边草地", "带井盖的柏油路",
    ]],
    "04_活山": [(n, lambda n=n: mountain_tile(n, True)) for n in [
        "有灌木的绿色山坡", "山路", "有藤蔓的山崖", "山洞入口", "有小瀑布的山",
    ]],
    "05_荒山": [(n, lambda n=n: mountain_tile(n, False)) for n in [
        "光秃的岩石山坡", "碎石山顶", "干裂的岩石表面", "长有枯枝的山", "荒芜的悬崖边",
    ]],
    "06_森林": [(n, lambda n=n: forest_tile(n)) for n in [
        "密集树群（俯视）", "稀疏树群", "草地上的树影", "森林小径", "长有小蘑菇的森林",
    ]],
    "07_村庄建筑": [(n, lambda n=n: village_tile(n)) for n in [
        "茅草屋顶", "木墙", "村庄围栏", "木门", "村庄水井",
    ]],
    "08_水域": [(n, lambda n=n: water_tile(n)) for n in [
        "平静的河面", "有波纹的流动河水", "有鹅卵石的浅水", "深水", "小池塘", "长有芦苇的水边",
    ]],
    "09_地形过渡": [(n, lambda n=n: transition_tile(n)) for n in [
        "草地与山的过渡", "草地与水的过渡", "路与森林的过渡", "荒山与草地的过渡", "村庄与路的过渡",
    ]],
    "10_互动道具": [(n, lambda n=n: prop_tile(n)) for n in [
        "木制路标", "小石碑", "篝火", "木桶", "破损的木车",
    ]],
    "11_农田": [(n, lambda n=n: farm_tile(n)) for n in [
        "整齐的麦田", "稻田", "菜地", "农田小路", "农田边缘的篱笆",
    ]],
    "12_花丛": [(n, lambda n=n: flower_tile(n)) for n in [
        "大片花丛", "野花丛", "带蝴蝶的花丛", "花丛小径", "花丛中的石头",
    ]],
    "13_沙漠": [(n, lambda n=n: desert_tile(n)) for n in [
        "沙地", "沙丘", "带仙人掌的沙地", "沙漠岩石", "沙漠中的枯树",
    ]],
    "14_雪地": [(n, lambda n=n: snow_tile(n)) for n in [
        "积雪覆盖的地面", "雪坡", "雪地小径", "雪堆", "雪中的岩石",
    ]],
    "15_海滩": [(n, lambda n=n: beach_tile(n)) for n in [
        "沙滩", "沙滩上的贝壳", "海边岩石", "海水浪花", "沙滩上的椰子树",
    ]],
    "16_城堡": [(n, lambda n=n: castle_tile(n)) for n in [
        "城堡城墙", "城堡塔楼", "城堡大门", "城堡内的石板路", "城堡花园",
    ]],
    "17_城镇街道": [(n, lambda n=n: town_tile(n)) for n in [
        "石板街道", "街道旁的房屋", "路灯", "街道上的摊位", "下水道入口",
    ]],
    "18_废墟": [(n, lambda n=n: ruin_tile(n)) for n in [
        "破损的墙壁", "倒塌的石柱", "废墟中的砖块", "废弃的建筑地基", "废墟中的宝箱",
    ]],
    "19_洞穴内部": [(n, lambda n=n: cave_tile(n)) for n in [
        "洞穴石壁", "洞穴地面的碎石", "洞穴中的火把", "洞穴岔路", "洞穴中的水池",
    ]],
    "20_魔法元素": [(n, lambda n=n: magic_tile(n)) for n in [
        "魔法阵", "发光的水晶", "漂浮的魔法符文", "魔法火焰", "魔法迷雾",
    ]],
    "21_陷阱": [(n, lambda n=n: trap_tile(n)) for n in [
        "地板尖刺", "压力板", "易碎的地砖", "陷阱门", "隐藏的暗箭",
    ]],
    "22_机关": [(n, lambda n=n: mechanism_tile(n)) for n in [
        "杠杆", "开关", "魔法封印", "转动的齿轮", "升降平台",
    ]],
    "23_怪物栖息地": [(n, lambda n=n: monster_tile(n)) for n in [
        "怪物巢穴入口", "怪物脚印", "怪物的骨头堆", "怪物的粪便", "怪物的爪痕",
    ]],
    "24_树木变体": [(n, lambda n=n: tree_tile(n)) for n in [
        "橡树", "松树", "枫树", "枯树", "被砍伐的树桩", "树上的鸟巢", "树藤缠绕的树",
    ]],
    "25_室内家具": [(n, lambda n=n: furniture_tile(n)) for n in [
        "桌子", "椅子", "床", "书架", "壁炉",
    ]],
}


def main() -> None:
    manifest: list[str] = []
    total = 0
    for folder, items in CATEGORIES.items():
        dest = OUT / folder
        dest.mkdir(parents=True, exist_ok=True)
        for name, gen in items:
            img = gen()
            path = dest / f"{name}.png"
            img.save(path, "PNG")
            manifest.append(f"{folder}/{name}.png")
            total += 1
            print(f"  [{total:3d}] {path.relative_to(OUT.parent)}")

    readme = OUT / "tile_manifest.txt"
    readme.write_text(
        "Ming Dynasty Game - Tile 图集清单\n"
        f"共 {total} 张，每张 32x32 像素 PNG\n"
        + ("=" * 40) + "\n" + "\n".join(manifest),
        encoding="utf-8",
    )
    print(f"\n完成！共生成 {total} 张 tile，输出目录: {OUT}")


if __name__ == "__main__":
    main()
