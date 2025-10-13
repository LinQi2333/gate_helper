import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class SceneConfig:
    """场景配置类"""
    def __init__(
        self,
        name: str,
        physical_width: float,
        offset_x: float,
        offset_y: float,
        image_path: str,
        x_direction: str = 'x+',
        y_direction: str = 'y+',
        reverse_xy: bool = False
    ):
        self.name = name
        self.physical_width = physical_width
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.image_path = image_path
        self.x_direction = x_direction
        self.y_direction = y_direction
        self.reverse_xy = reverse_xy

class MapVisualizer:
    """地图可视化工具"""
    
    # 场景ID映射到名称
    SITE_ID_TO_NAME = {
        1: "マイホーム",
        2: "1F",
        3: "2F",
        4: "3F",
        5: "さいしょの原っぱ",
        6: "願いの砂浜",
        7: "彩りの花畑",
        8: "忘れ去られた場所",
    }
    
    # 预定义的场景配置
    SCENES = {
        5: SceneConfig(  # さいしょの原っぱ
            name="さいしょの原っぱ",
            physical_width=33.333,
            offset_x=0,
            offset_y=-40,
            image_path="img/grassland.png",
            x_direction='x-',
            y_direction='y-',
            reverse_xy=True
        ),
        7: SceneConfig(  # 彩りの花畑
            name="彩りの花畑",
            physical_width=24.806,
            offset_x=-62.015,
            offset_y=20.672,
            image_path="img/flowergarden.png",
            x_direction='x-',
            y_direction='y-',
            reverse_xy=True
        ),
        6: SceneConfig(  # 願いの砂浜
            name="願いの砂浜",
            physical_width=20.513,
            offset_x=0,
            offset_y=80,
            image_path="img/beach.png",
            x_direction='x+',
            y_direction='y-',
            reverse_xy=False
        ),
        8: SceneConfig(  # 忘れ去られた場所
            name="忘れ去られた場所",
            physical_width=21.333,
            offset_x=0,
            offset_y=-106.667,
            image_path="img/memorialplace.png",
            x_direction='x+',
            y_direction='y-',
            reverse_xy=False
        )
    }
    
    # Fixture颜色映射
    FIXTURE_COLORS = {
        112: (249, 249, 249),
        1001: (218, 109, 66), 1002: (218, 109, 66), 1003: (218, 109, 66), 1004: (218, 109, 66),
        2001: (135, 134, 133), 2002: (213, 117, 10), 2003: (213, 213, 213),
        2004: (167, 199, 203), 2005: (153, 51, 204),
        3001: (201, 90, 73),
        4001: (248, 114, 154), 4002: (248, 114, 154), 4003: (248, 114, 154), 4004: (248, 114, 154),
        4005: (248, 114, 154), 4006: (248, 114, 154), 4007: (248, 114, 154), 4008: (248, 114, 154),
        4009: (248, 114, 154), 4010: (248, 114, 154), 4011: (248, 114, 154), 4012: (248, 114, 154),
        4013: (248, 114, 154), 4014: (248, 114, 154), 4015: (248, 114, 154), 4016: (248, 114, 154),
        4017: (248, 114, 154), 4018: (248, 114, 154), 4019: (248, 114, 154), 4020: (248, 114, 154),
        5001: (246, 245, 242), 5002: (246, 245, 242), 5003: (246, 245, 242), 5004: (246, 245, 242),
        5101: (246, 245, 242), 5102: (246, 245, 242), 5103: (246, 245, 242), 5104: (246, 245, 242),
        6001: (111, 78, 55),
        7001: (165, 217, 255),
    }
    
    def __init__(
        self,
        id: str,
        json_file: str,
        base_folder: str = ".",
        icon_folder: str = "icon/Texture2D",
        output_folder: str = "output",
        point_size: int = 5,
        font_size: int = 10
    ):
        self.id = id
        self.json_file = Path(json_file)
        self.base_folder = Path(base_folder)
        self.icon_folder = Path(icon_folder)
        self.output_folder = Path(output_folder)
        self.point_size = point_size
        self.font_size = font_size
        
        self.output_folder.mkdir(exist_ok=True, parents=True)
        
        # 加载字体
        try:
            self.font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                self.font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
            except:
                self.font = ImageFont.load_default()
    
    def parse_raw_map_data(self, map_data: Dict) -> List[Dict]:
        """
        将原始 API 数据转换为处理格式
        合并同一位置的 fixture 和 resources
        """
        fixtures = map_data.get("userMysekaiSiteHarvestFixtures", [])
        resources = map_data.get("userMysekaiSiteHarvestResourceDrops", [])
        
        # 按位置分组资源
        location_map = defaultdict(lambda: {"fixture_id": None, "rewards": defaultdict(lambda: defaultdict(int))})
        
        # 处理 fixtures
        for fixture in fixtures:
            if fixture.get("userMysekaiSiteHarvestFixtureStatus") == "spawned":
                pos = (fixture["positionX"], fixture["positionZ"])
                location_map[pos]["fixture_id"] = fixture["mysekaiSiteHarvestFixtureId"]
        
        # 处理 resources
        for resource in resources:
            pos = (resource["positionX"], resource["positionZ"])
            resource_type = resource["resourceType"]
            resource_id = resource["resourceId"]
            quantity = resource["quantity"]
            
            # 累加同一位置同一类型同一ID的资源
            location_map[pos]["rewards"][resource_type][resource_id] += quantity
        
        # 转换为列表格式
        result = []
        for (x, z), data in location_map.items():
            if data["fixture_id"] is not None:  # 只处理有 fixture 的位置
                result.append({
                    "location": [x, z],
                    "fixtureId": data["fixture_id"],
                    "reward": dict(data["rewards"])  # 转换为普通字典
                })
        
        return result
    
    def game_to_pixel(
        self, 
        game_x: float, 
        game_y: float, 
        scene: SceneConfig, 
        bg_width: int, 
        bg_height: int
    ) -> Tuple[int, int]:
        """将游戏坐标转换为像素坐标"""
        # 计算原点位置（背景图中心 + 偏移）
        origin_x = bg_width / 2 + scene.offset_x
        origin_y = bg_height / 2 + scene.offset_y
        
        # 如果需要交换XY轴
        if scene.reverse_xy:
            game_x, game_y = game_y, game_x
        
        # 根据方向计算像素坐标
        if scene.x_direction == 'x+':
            display_x = origin_x + game_x * scene.physical_width
        else:
            display_x = origin_x - game_x * scene.physical_width
        
        if scene.y_direction == 'y+':
            display_y = origin_y + game_y * scene.physical_width
        else:
            display_y = origin_y - game_y * scene.physical_width
        
        return int(display_x), int(display_y)
    
    def load_icon(self, resource_type: str, resource_id: int, size: int = 20) -> Optional[Image.Image]:
        """加载资源图标"""
        # 图标文件名映射
        icon_mappings = {
            'mysekai_material': {
                1: 'item_wood_1.png', 2: 'item_wood_2.png', 3: 'item_wood_3.png',
                4: 'item_wood_4.png', 5: 'item_wood_5.png', 6: 'item_mineral_1.png',
                7: 'item_mineral_2.png', 8: 'item_mineral_3.png', 9: 'item_mineral_4.png',
                10: 'item_mineral_5.png', 11: 'item_mineral_6.png', 12: 'item_mineral_7.png',
                13: 'item_junk_1.png', 14: 'item_junk_2.png', 15: 'item_junk_3.png',
                16: 'item_junk_4.png', 17: 'item_junk_5.png', 18: 'item_junk_6.png',
                19: 'item_junk_7.png', 20: 'item_plant_1.png', 21: 'item_plant_2.png',
                22: 'item_plant_3.png', 23: 'item_plant_4.png', 24: 'item_tone_8.png',
                32: 'item_junk_8.png', 33: 'item_mineral_8.png', 34: 'item_junk_9.png',
                61: 'item_junk_10.png', 62: 'item_junk_11.png', 63: 'item_junk_12.png',
                64: 'item_mineral_9.png', 65: 'item_mineral_10.png',
            },
            'mysekai_item': {
                7: 'item_blueprint_fragment.png',
            },
            'mysekai_music_record': 'item_surplus_music_record.png',
        }
        
        icon_name = None
        if resource_type == 'mysekai_music_record':
            icon_name = icon_mappings['mysekai_music_record']
        elif resource_type in icon_mappings and resource_id in icon_mappings[resource_type]:
            icon_name = icon_mappings[resource_type][resource_id]
        
        if icon_name:
            icon_path = self.icon_folder / icon_name
            if icon_path.exists():
                icon = Image.open(icon_path).convert('RGBA')
                icon = icon.resize((size, size), Image.Resampling.LANCZOS)
                return icon
        
        return None
    
    def draw_point_with_rewards(
        self,
        draw: ImageDraw.Draw,
        background: Image.Image,
        x: int,
        y: int,
        fixture_id: int,
        reward: Dict,
        scene: SceneConfig
    ):
        """绘制资源点和奖励"""
        # 获取fixture颜色，默认黑色
        color = self.FIXTURE_COLORS.get(fixture_id, (0, 0, 0))
        
        # 绘制圆点
        draw.ellipse(
            [x - self.point_size, y - self.point_size, 
             x + self.point_size, y + self.point_size],
            fill=color,
            outline=(0, 0, 0),
            width=2
        )
        
        # 绘制奖励图标
        self.draw_rewards(background, x, y, reward, scene)
    
    def create_missing_icon(self, size: int = 20) -> Image.Image:
        """创建缺失图标的占位图"""
        icon = Image.new('RGBA', (size, size), (200, 200, 200, 255))
        draw = ImageDraw.Draw(icon)
        # 绘制"miss"文字
        text = "miss"
        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2
        draw.text((text_x, text_y), text, fill=(100, 100, 100), font=self.font)
        return icon
    
    def draw_rewards(
        self,
        background: Image.Image,
        x: int,
        y: int,
        reward: Dict,
        scene: SceneConfig
    ):
        """绘制奖励物品列表"""
        icon_size = 20
        offset = scene.physical_width * 0.3 if not scene.reverse_xy else scene.physical_width * 0.3
        
        # 收集所有物品
        items = []
        for category, category_items in reward.items():
            for item_id, quantity in category_items.items():
                icon = self.load_icon(category, int(item_id), icon_size)
                if icon:
                    items.append((icon, quantity))
        
        if not items:
            return
        
        # 计算背景尺寸和位置
        if scene.reverse_xy:
            # 横向排列
            total_width = len(items) * icon_size
            total_height = icon_size
            start_x = int(x + offset)
            start_y = int(y - icon_size / 2)
        else:
            # 纵向排列
            total_width = icon_size
            total_height = len(items) * icon_size
            start_x = int(x + offset)
            start_y = int(y)
        
        # 绘制半透明灰色背景
        overlay = Image.new('RGBA', background.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [start_x, start_y, start_x + total_width, start_y + total_height],
            fill=(138, 138, 138, 180)
        )
        background.paste(Image.alpha_composite(background, overlay), (0, 0))
        
        # 绘制物品图标和数量
        for i, (icon, quantity) in enumerate(items):
            if scene.reverse_xy:
                icon_x = start_x + i * icon_size
                icon_y = start_y
            else:
                icon_x = start_x
                icon_y = start_y + i * icon_size
            
            # 贴图标
            background.paste(icon, (icon_x, icon_y), icon)
            
            # 绘制数量（如果大于1）
            if quantity > 1:
                draw = ImageDraw.Draw(background)
                text = str(quantity)
                # 右下角位置
                text_x = icon_x + icon_size - 8
                text_y = icon_y + icon_size - 10
                # 绘制白色半透明圆形背景
                bbox = draw.textbbox((text_x, text_y), text, font=self.font)
                draw.ellipse([bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2], fill=(255, 255, 255, 128))
                # 绘制黑色数字
                draw.text((text_x, text_y), text, fill=(0, 0, 0), font=self.font)
    
    def process_map(self, map_data: Dict, site_id: int):
        """处理单个地图"""
        if site_id not in self.SCENES:
            print(f"Warning: No scene config for site {site_id}, skipping...")
            return
        
        scene = self.SCENES[site_id]
        scene_name = self.SITE_ID_TO_NAME.get(site_id, f"Site_{site_id}")
        print(f"Processing {scene_name} (ID: {site_id})...")
        
        # 解析原始数据
        processed_data = self.parse_raw_map_data(map_data)
        
        # 加载背景图
        bg_path = self.base_folder / scene.image_path
        if not bg_path.exists():
            print(f"  Error: Background image not found: {bg_path}")
            return
        
        background = Image.open(bg_path).convert('RGBA')
        bg_width, bg_height = background.size
        draw = ImageDraw.Draw(background)
        
        # 处理每个资源点
        for point in processed_data:
            location = point.get('location', [0, 0])
            fixture_id = point.get('fixtureId', 0)
            reward = point.get('reward', {})
            
            # 转换坐标
            x, y = self.game_to_pixel(location[0], location[1], scene, bg_width, bg_height)
            
            # 绘制点和奖励
            self.draw_point_with_rewards(draw, background, x, y, fixture_id, reward, scene)
        
        # 保存结果
        output_path = self.output_folder / f"{self.id}_map_{site_id}.png"
        background.save(output_path)
        print(f"  Saved to {output_path}")
        print(f"  Processed {len(processed_data)} resource points")
    
    def process_all(self):
        """处理所有地图"""
        print("Loading JSON data...")
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 查找地图数据
        maps_data = None
        
        # 尝试从原始 API 数据中提取
        if "updatedResources" in data:
            if "userMysekaiHarvestMaps" in data["updatedResources"]:
                maps_data = data["updatedResources"]["userMysekaiHarvestMaps"]
        elif "userMysekaiHarvestMaps" in data:
            maps_data = data["userMysekaiHarvestMaps"]
        
        if not maps_data:
            print("Error: Could not find map data in JSON")
            print("Expected path: updatedResources.userMysekaiHarvestMaps")
            return
        
        print(f"Found {len(maps_data)} maps")
        
        # 处理每个地图
        for map_data in maps_data:
            site_id = map_data.get("mysekaiSiteId")
            if site_id:
                self.process_map(map_data, site_id)
        
        print("\nAll done!")