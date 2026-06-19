# -*- coding: utf-8 -*-
"""
Generate 16 historical scene JSON files for Ming Dynasty RPG.
Each map is 40x30, uses at most 6 unique tile types, and forms a directed/bidirectional graph.
"""

import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "scenes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Map dimensions
W = 40
H = 30

def make_empty_grid(char: str) -> list[str]:
    return [char * W for _ in range(H)]

def draw_horizontal_road(grid: list[str], y: int, char: str) -> list[str]:
    new_grid = []
    for idx, row in enumerate(grid):
        if idx == y:
            new_grid.append(char * W)
        else:
            new_grid.append(row)
    return new_grid

def draw_vertical_road(grid: list[str], x: int, char: str) -> list[str]:
    new_grid = []
    for row in grid:
        new_row = row[:x] + char + row[x+1:]
        new_grid.append(new_row)
    return new_grid

def draw_border_trees(grid: list[str], char: str, open_dirs: list[str]) -> list[str]:
    new_grid = []
    for r_idx, row in enumerate(grid):
        new_row = list(row)
        for c_idx in range(W):
            # Check if border
            is_border = (r_idx == 0 or r_idx == H - 1 or c_idx == 0 or c_idx == W - 1)
            if is_border:
                # Check if we should keep it open for transitions
                if r_idx == 0 and "north" in open_dirs and 12 <= c_idx <= 16:
                    continue
                if r_idx == H - 1 and "south" in open_dirs and 12 <= c_idx <= 16:
                    continue
                if c_idx == 0 and "west" in open_dirs and 13 <= r_idx <= 17:
                    continue
                if c_idx == W - 1 and "east" in open_dirs and 13 <= r_idx <= 17:
                    continue
                new_row[c_idx] = char
        new_grid.append("".join(new_row))
    return new_grid

# Define the 16 maps
SCENES_DATA = {
    "huangjuesi": {
        "name": "皇觉寺 (Huangjue Temple)",
        "theme": "temple",
        "tiles": ["g", "r", "v", "T", "R", "W"], # 6 tiles
        "open_dirs": ["west", "east"],
        "connections": {
            "west": {"map_id": "north", "start_x": 38, "start_y": 15},
            "east": {"map_id": "huaixi", "start_x": 1, "start_y": 15}
        },
        "npcs": [
            {
                "id": "abbot",
                "name": "主持大师",
                "sprite": "monk",
                "x": 20,
                "y": 10,
                "dialogue": [
                    "阿弥陀佛，重八。元兵作乱，寺庙也难保全。",
                    "你且带上这口破碗，下山化缘去吧。记住，心中有佛，处处皆是修行。"
                ]
            }
        ],
        "chests": [
            {
                "x": 25,
                "y": 8,
                "opened": False,
                "item": "香烛",
                "dialogue": "你打开了寺庙偏殿的宝箱，获得了【香烛】！"
            }
        ]
    },
    "huaixi": {
        "name": "淮西 (Huaixi Plains)",
        "theme": "plains",
        "tiles": ["g", "h", "r", "v", "K", "F"], # 6 tiles
        "open_dirs": ["west", "north"],
        "connections": {
            "west": {"map_id": "huangjuesi", "start_x": 38, "start_y": 15},
            "north": {"map_id": "henan", "start_x": 14, "start_y": 28}
        },
        "npcs": [
            {
                "id": "huaixi_peasant",
                "name": "淮西百姓",
                "sprite": "farmer",
                "x": 18,
                "y": 12,
                "dialogue": [
                    "淮西大旱，颗粒无收，官府还要强征暴敛！",
                    "听说不少乡亲都去投奔红巾军了，这日子真是不给活路啊！"
                ]
            }
        ],
        "chests": [
            {
                "x": 8,
                "y": 8,
                "opened": False,
                "item": "霉变的小麦",
                "dialogue": "你在荒废的农舍里找到了【霉变的小麦】。虽然发霉，但乱世中也是口粮。"
            }
        ]
    },
    "henan": {
        "name": "河南 (Henan Plains)",
        "theme": "drylands",
        "tiles": ["h", "s", "r", "v", "K", "Y"], # 6 tiles
        "open_dirs": ["south", "east"],
        "connections": {
            "south": {"map_id": "huaixi", "start_x": 14, "start_y": 1},
            "east": {"map_id": "miaoshan", "start_x": 1, "start_y": 15}
        },
        "npcs": [
            {
                "id": "henan_refugee",
                "name": "河南流民",
                "sprite": "merchant",
                "x": 22,
                "y": 18,
                "dialogue": [
                    "北国兵荒马乱，红巾军起义了！到处都在打仗！",
                    "小师父，看你拿着个破碗，还是快些往南边走吧！"
                ]
            }
        ],
        "chests": [
            {
                "x": 30,
                "y": 10,
                "opened": False,
                "item": "破旧的布鞋",
                "dialogue": "你在一块古老石碑旁捡到了【破旧的布鞋】。"
            }
        ]
    },
    "miaoshan": {
        "name": "定远妙山 (Dingyuan Miaoshan)",
        "theme": "mountains",
        "tiles": ["g", "s", "r", "v", "T", "P"], # 6 tiles
        "open_dirs": ["west", "south"],
        "connections": {
            "west": {"map_id": "henan", "start_x": 38, "start_y": 15},
            "south": {"map_id": "lvpaizhai", "start_x": 14, "start_y": 1}
        },
        "npcs": [
            {
                "id": "miaoshan_soldier",
                "name": "妙山新兵",
                "sprite": "friend",
                "x": 20,
                "y": 20,
                "dialogue": [
                    "朱将军！我们听闻您的威名，特来投奔！",
                    "妙山地势险要，是招兵买马的好地方！"
                ]
            }
        ],
        "chests": [
            {
                "x": 10,
                "y": 5,
                "opened": False,
                "item": "生锈的铁剑",
                "dialogue": "你在山顶的松树下发现了【生锈的铁剑】！"
            }
        ]
    },
    "lvpaizhai": {
        "name": "定远驴牌寨 (Dingyuan Lvpai Camp)",
        "theme": "camp",
        "tiles": ["g", "r", "v", "F", "B", "U"], # 6 tiles
        "open_dirs": ["north", "east"],
        "connections": {
            "north": {"map_id": "miaoshan", "start_x": 14, "start_y": 28},
            "east": {"map_id": "hezhou", "start_x": 1, "start_y": 15}
        },
        "npcs": [
            {
                "id": "bandit_leader",
                "name": "驴牌寨寨主",
                "sprite": "chang",
                "x": 25,
                "y": 15,
                "dialogue": [
                    "朱公子，俺们这寨里有三千好汉，如今愿意全部归顺红巾军！",
                    "愿随朱将军共图大业，推翻元廷！"
                ]
            }
        ],
        "chests": [
            {
                "x": 32,
                "y": 22,
                "opened": False,
                "item": "行军干粮",
                "dialogue": "你在军用木桶旁找到了【行军干粮】！"
            }
        ]
    },
    "hezhou": {
        "name": "和州 (Hezhou Port)",
        "theme": "port",
        "tiles": ["g", "w", "b", "r", "v", "T"], # 6 tiles
        "open_dirs": ["west", "south"],
        "connections": {
            "west": {"map_id": "lvpaizhai", "start_x": 38, "start_y": 15},
            "south": {"map_id": "taiping", "start_x": 14, "start_y": 1}
        },
        "npcs": [
            {
                "id": "boatman",
                "name": "渡口船夫",
                "sprite": "farmer",
                "x": 10,
                "y": 18,
                "dialogue": [
                    "朱将军，大军已在和州集结，数万将士随时可以渡江！",
                    "长江天险虽固，但也挡不住我军的熊熊烈火！"
                ]
            }
        ],
        "chests": [
            {
                "x": 5,
                "y": 5,
                "opened": False,
                "item": "皮甲",
                "dialogue": "你在渡口货箱里发现了【皮甲】！"
            }
        ]
    },
    "taiping": {
        "name": "太平府 (Taiping Prefecture)",
        "theme": "city",
        "tiles": ["g", "r", "v", "R", "W", "D"], # 6 tiles
        "open_dirs": ["north", "east"],
        "connections": {
            "north": {"map_id": "hezhou", "start_x": 14, "start_y": 28},
            "east": {"map_id": "yingtian", "start_x": 1, "start_y": 15}
        },
        "npcs": [
            {
                "id": "taiping_scholar",
                "name": "太平名士",
                "sprite": "merchant",
                "x": 20,
                "y": 12,
                "dialogue": [
                    "朱帅进城后，秋毫无犯，开仓放粮，真乃仁义之师！",
                    "太平百姓无不箪食壶浆，以迎王师！"
                ]
            }
        ],
        "chests": [
            {
                "x": 30,
                "y": 8,
                "opened": False,
                "item": "精钢短刀",
                "dialogue": "你打开了官衙前的宝箱，获得了【精钢短刀】！"
            }
        ]
    },
    "yingtian": {
        "name": "应天府 (Yingtian Capital)",
        "theme": "capital",
        "tiles": ["g", "r", "v", "R", "W", "D"], # 6 tiles
        "open_dirs": ["west", "south"],
        "connections": {
            "west": {"map_id": "taiping", "start_x": 38, "start_y": 15},
            "south": {"map_id": "huizhou", "start_x": 14, "start_y": 1}
        },
        "npcs": [
            {
                "id": "liubowen",
                "name": "刘伯温",
                "sprite": "monk",
                "x": 15,
                "y": 10,
                "dialogue": [
                    "主公，应天乃帝王之基。当‘高筑墙，广积粮，缓称王’。",
                    "北御元军，西防陈友谅，东拒张士诚，方可立于不败之地。"
                ]
            }
        ],
        "chests": [
            {
                "x": 25,
                "y": 22,
                "opened": False,
                "item": "大明军旗",
                "dialogue": "你获得了【大明军旗】！猎猎军旗，誓扫元廷！"
            }
        ]
    },
    "huizhou": {
        "name": "徽州 (Huizhou Hills)",
        "theme": "huizhou",
        "tiles": ["g", "s", "r", "v", "R", "W"], # 6 tiles
        "open_dirs": ["north", "east"],
        "connections": {
            "north": {"map_id": "yingtian", "start_x": 14, "start_y": 28},
            "east": {"map_id": "zhedong", "start_x": 1, "start_y": 15}
        },
        "npcs": [
            {
                "id": "zhusheng",
                "name": "朱升",
                "sprite": "elder",
                "x": 18,
                "y": 15,
                "dialogue": [
                    "徽州山川险固，百姓淳朴。主公在此屯兵积粮，可保后路无忧。",
                    "天下大势，终将归于有德之人。"
                ]
            }
        ],
        "chests": [
            {
                "x": 32,
                "y": 5,
                "opened": False,
                "item": "徽州贡菊",
                "dialogue": "你在徽派民居旁找到了【徽州贡菊】。"
            }
        ]
    },
    "zhedong": {
        "name": "浙东 (Zhedong Hills)",
        "theme": "zhedong",
        "tiles": ["g", "f", "r", "v", "M", "T"], # 6 tiles
        "open_dirs": ["west", "south"],
        "connections": {
            "west": {"map_id": "huizhou", "start_x": 38, "start_y": 15},
            "south": {"map_id": "jinhua", "start_x": 14, "start_y": 1}
        },
        "npcs": [
            {
                "id": "zhedong_girl",
                "name": "浙东蚕妇",
                "sprite": "farmer",
                "x": 22,
                "y": 12,
                "dialogue": [
                    "战乱连连，只盼朱将军早日平定江南，让我们能安稳养蚕织布。",
                    "听说浙东名士刘基、宋濂都去应天辅佐您了，真是太好了！"
                ]
            }
        ],
        "chests": [
            {
                "x": 8,
                "y": 22,
                "opened": False,
                "item": "丝绸",
                "dialogue": "你获得了【丝绸】！"
            }
        ]
    },
    "jinhua": {
        "name": "金华 (Jinhua)",
        "theme": "jinhua",
        "tiles": ["g", "r", "v", "m", "i", "F"], # 6 tiles
        "open_dirs": ["north", "west"],
        "connections": {
            "north": {"map_id": "zhedong", "start_x": 14, "start_y": 28},
            "west": {"map_id": "poyanghu", "start_x": 38, "start_y": 15}
        },
        "npcs": [
            {
                "id": "jinhua_farmer",
                "name": "金华农夫",
                "sprite": "farmer",
                "x": 15,
                "y": 18,
                "dialogue": [
                    "朱大帅！这是俺们金华特产的火腿，香气扑鼻，送给将士们做军粮！",
                    "祝大帅早日扫平群雄，建立太平盛世！"
                ]
            }
        ],
        "chests": [
            {
                "x": 28,
                "y": 8,
                "opened": False,
                "item": "金华火腿",
                "dialogue": "你获得了【金华火腿】！这可是绝佳的补给品。"
            }
        ]
    },
    "poyanghu": {
        "name": "鄱阳湖 (Poyang Lake)",
        "theme": "lake",
        "tiles": ["w", "o", "b", "g", "r", "v"], # 6 tiles
        "open_dirs": ["east", "north"],
        "connections": {
            "east": {"map_id": "jinhua", "start_x": 1, "start_y": 15},
            "north": {"map_id": "suzhou", "start_x": 14, "start_y": 28}
        },
        "npcs": [
            {
                "id": "hancheng",
                "name": "大将韩成",
                "sprite": "chang",
                "x": 12,
                "y": 16,
                "dialogue": [
                    "主公！陈友谅巨舰遮天蔽日，我军形势危急！",
                    "末将与主公相貌相似，愿穿上主公金甲，代主公投江受死，以安军心！",
                    "主公当保重龙体，大明江山全系于主公一人！"
                ]
            }
        ],
        "chests": [
            {
                "x": 30,
                "y": 5,
                "opened": False,
                "item": "避水珠",
                "dialogue": "你在湖边礁石缝中找到了传说中的【避水珠】！"
            }
        ]
    },
    "suzhou": {
        "name": "苏州 (Suzhou Water Town)",
        "theme": "watertown",
        "tiles": ["g", "w", "b", "r", "v", "R"], # 6 tiles
        "open_dirs": ["south", "north"],
        "connections": {
            "south": {"map_id": "poyanghu", "start_x": 14, "start_y": 1},
            "north": {"map_id": "yuandadu", "start_x": 14, "start_y": 28}
        },
        "npcs": [
            {
                "id": "suzhou_citizen",
                "name": "苏州百姓",
                "sprite": "merchant",
                "x": 22,
                "y": 14,
                "dialogue": [
                    "诚王张士诚待我们苏州百姓极好，可惜他终究偏安一隅，无大志。",
                    "如今大明王师进城，只盼莫要惊扰了这姑苏城的繁华。"
                ]
            }
        ],
        "chests": [
            {
                "x": 8,
                "y": 8,
                "opened": False,
                "item": "苏绣锦缎",
                "dialogue": "你获得了【苏绣锦缎】！"
            }
        ]
    },
    "yuandadu": {
        "name": "元大都 (Yuan Dadu Capital)",
        "theme": "palace",
        "tiles": ["g", "r", "v", "R", "W", "D"], # 6 tiles
        "open_dirs": ["south", "west"],
        "connections": {
            "south": {"map_id": "suzhou", "start_x": 14, "start_y": 1},
            "west": {"map_id": "sichuan", "start_x": 38, "start_y": 15}
        },
        "npcs": [
            {
                "id": "xuda_general",
                "name": "大将军徐达",
                "sprite": "friend",
                "x": 20,
                "y": 15,
                "dialogue": [
                    "上位！臣已率北伐大军攻克元大都，顺帝北逃漠北！",
                    "百年胡运，一朝而终！中原光复，请上位即皇帝位，昭告天下！"
                ]
            }
        ],
        "chests": [
            {
                "x": 20,
                "y": 5,
                "opened": False,
                "item": "传国玉玺",
                "dialogue": "你打开了元廷大殿的龙椅宝箱，获得了【传国玉玺】！你终于登基称帝，建立大明！"
            }
        ]
    },
    "sichuan": {
        "name": "四川 (Sichuan Basin)",
        "theme": "sichuan",
        "tiles": ["g", "s", "r", "v", "P", "K"], # 6 tiles
        "open_dirs": ["east", "south"],
        "connections": {
            "east": {"map_id": "yuandadu", "start_x": 1, "start_y": 15},
            "south": {"map_id": "yunnan", "start_x": 14, "start_y": 1}
        },
        "npcs": [
            {
                "id": "sichuan_elder",
                "name": "蜀中父老",
                "sprite": "elder",
                "x": 18,
                "y": 12,
                "dialogue": [
                    "蜀主明玉珍将军已逝，其子年幼。大明王师入川，蜀中百姓愿归顺大明！",
                    "蜀道虽难，也难挡大明一统乾坤之志！"
                ]
            }
        ],
        "chests": [
            {
                "x": 30,
                "y": 20,
                "opened": False,
                "item": "蜀锦",
                "dialogue": "你获得了【蜀锦】！"
            }
        ]
    },
    "yunnan": {
        "name": "云南 (Yunnan Border)",
        "theme": "yunnan",
        "tiles": ["g", "f", "r", "v", "M", "Y"], # 6 tiles
        "open_dirs": ["north"],
        "connections": {
            "north": {"map_id": "sichuan", "start_x": 14, "start_y": 28}
        },
        "npcs": [
            {
                "id": "muying",
                "name": "大将沐英",
                "sprite": "chang",
                "x": 20,
                "y": 15,
                "dialogue": [
                    "皇上！臣沐英已率军荡平梁王余孽，收复云南全境！",
                    "臣愿世代镇守云南，保我大明西南边疆永固，万世太平！"
                ]
            }
        ],
        "chests": [
            {
                "x": 10,
                "y": 10,
                "opened": False,
                "item": "普洱茶砖",
                "dialogue": "你获得了【普洱茶砖】！"
            }
        ]
    }
}

def main() -> None:
    for scene_id, data in SCENES_DATA.items():
        # Build base ground map using the first tile as default
        bg_tile = data["tiles"][0]
        ground = make_empty_grid(bg_tile)
        
        # Draw roads based on open directions
        road_h_tile = data["tiles"][1] if len(data["tiles"]) > 1 else bg_tile
        road_v_tile = data["tiles"][2] if len(data["tiles"]) > 2 else bg_tile
        
        # If horizontal connection exists, draw horizontal road
        if "west" in data["open_dirs"] or "east" in data["open_dirs"]:
            ground = draw_horizontal_road(ground, 15, road_h_tile)
            
        # If vertical connection exists, draw vertical road
        if "north" in data["open_dirs"] or "south" in data["open_dirs"]:
            ground = draw_vertical_road(ground, 14, road_v_tile)
            
        # Build obstacle map
        obstacle = make_empty_grid(".")
        
        # Draw border trees
        tree_tile = data["tiles"][3] if len(data["tiles"]) > 3 else "."
        if tree_tile != ".":
            obstacle = draw_border_trees(obstacle, tree_tile, data["open_dirs"])
            
        # Add some decorative obstacles in the corners
        dec_tile_1 = data["tiles"][4] if len(data["tiles"]) > 4 else "."
        dec_tile_2 = data["tiles"][5] if len(data["tiles"]) > 5 else "."
        
        # Let's place some decorations safely away from the roads (col 14, row 15)
        if dec_tile_1 != ".":
            # Avoid overwriting border or roads
            obstacle[5] = obstacle[5][:5] + dec_tile_1 + obstacle[5][6:]
            obstacle[22] = obstacle[22][:25] + dec_tile_1 + obstacle[22][26:]
        if dec_tile_2 != ".":
            obstacle[8] = obstacle[8][:32] + dec_tile_2 + obstacle[8][33:]
            obstacle[18] = obstacle[8][:8] + dec_tile_2 + obstacle[18][9:]
            
        # Create JSON structure
        scene_json = {
            "name": data["name"],
            "ground": ground,
            "obstacle": obstacle,
            "connections": data["connections"],
            "npcs": data["npcs"],
            "chests": data["chests"]
        }
        
        # Save to file
        dest_path = OUT_DIR / f"{scene_id}.json"
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(scene_json, f, ensure_ascii=False, indent=2)
            
        print(f"Generated scene JSON: {dest_path.relative_to(OUT_DIR.parent.parent)}")

if __name__ == "__main__":
    main()
