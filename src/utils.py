from pathlib import Path
import json
import requests
from .exception import FileDownloadError, UserError, NotFoundError
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class Utils:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.bond_path = self.base_path / "userdata" / "bond.json"

        self.gate_material_path = self.base_path / "data" / "mysekaiGateMaterialGroups.json"
        self.material_path = self.base_path / "data" / "mysekaiMaterials.json"

        self.blueprints_path = self.base_path / "data" / "mysekaiBlueprints.json"
        self.blueprints_map_path = self.base_path / "data" / "mysekaiFixtures.json"

        self.harvest_path = self.base_path / "data" / "mysekaiSiteHarvestFixtures.json"

        self.weather_path = self.base_path / "data" / "mysekaiPhenomenas.json"
        self.memorial_translate = self.base_path / "data" / "reference.json"

        self.sub_path = self.base_path / "data" / "usersubs.json"
    
    def bond_user(self, user_id: str, uid: str) -> None:
        if not self.bond_path.exists():
            with open(self.bond_path, "w", encoding = "utf-8") as f:
                json.dump([], f)
        with open(self.bond_path, "r", encoding = "utf-8") as f:
            data = json.load(f)

        updated = False
        for item in data:
            if user_id in item:
                item[user_id] = uid
                updated = True
                break

        if not updated:
            new_record = {user_id : uid}
            data.append(new_record)

        with open(self.bond_path, "w", encoding = "utf-8") as f:
            json.dump(data, f, indent = 4)
    
    def bond_sub(self, user_id: str, sub_id: list) -> None:
        if not self.sub_path.exists():
            with open(self.sub_path, "w", encoding = "utf-8") as f:
                json.dump([], f)
        with open(self.sub_path, "r", encoding = "utf-8") as f:
            data = json.load(f)
        
        updated = False
        for item in data:
            if user_id in item:
                item[user_id] = sub_id
                updated = True
                break
        if not updated:
            new_record = {user_id : sub_id}
            data.append(new_record)
        
        with open(self.sub_path, "w", encoding = "utf-8") as f:
            json.dump(data, f, indent = 4)
    
    def get_user_data(self, user_id: str) -> None:
        with open(self.bond_path, "r", encoding = "utf-8") as f:
            data = json.load(f)
        found = False
        for item in data:
            if user_id in item:
                uid = item[user_id]
                found = True
                break

        if not found:
            raise UserError("未绑定用户，使用指令[！绑定 uid]进行绑定")
        
        json_path = self.base_path / "data" / f"user_{user_id}.json"
        url = f"api" # configure it if you need

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(json_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
        else:
            if response.status_code == 404:
                raise FileDownloadError("未找到用户数据，请确认你上传的是suite数据且勾选公开API选项")
            else:
                raise FileDownloadError("用户数据下载失败，请使用反馈功能反馈")
            
    def get_user_ms_data(self, user_id: str) -> None:
        with open(self.bond_path, "r", encoding = "utf-8") as f:
            data = json.load(f)
        found = False
        for item in data:
            if user_id in item:
                uid = item[user_id]
                found = True
                break

        if not found:
            raise UserError("未绑定用户，使用指令[！绑定 uid]进行绑定")
        
        ms_json_path = self.base_path / "data" / f'user_{user_id}_ms.json'
        ms_url = f"api" # configure it if you need

        response_ms = requests.get(ms_url)
        if response_ms.status_code == 200:
            data = response_ms.json()
            with open(ms_json_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
        else:
            if response_ms.status_code == 404:
                raise FileDownloadError("未找到用户数据，请确认你上传的是mysekai数据且勾选公开API选项")
            else:
                raise FileDownloadError("用户ms数据下载失败，请使用反馈功能反馈")
    
    def get_gate_information(self) -> None:
        url = f"https://raw.githubusercontent.com/Team-Haruki/haruki-sekai-master/main/master/mysekaiGateMaterialGroups.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(self.gate_material_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
        else:
            raise FileDownloadError("升级材料下载失败，若多次重试仍然失败，请使用反馈功能反馈")
        
    def get_material_map(self) -> None:
        url = f"https://raw.githubusercontent.com/Team-Haruki/haruki-sekai-master/main/master/mysekaiMaterials.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(self.material_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
        else:
            raise FileDownloadError("材料映射下载失败，若多次重试仍然失败，请使用反馈功能反馈")
    
    def get_blueprints_infomation(self) -> None:
        url = f"https://raw.githubusercontent.com/Team-Haruki/haruki-sekai-master/main/master/mysekaiBlueprints.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(self.blueprints_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
        else:
            raise FileDownloadError("蓝图信息下载失败，若多次重试仍然失败，请使用反馈功能反馈")

    def get_blueprints_map(self) -> None:
        url = f"https://raw.githubusercontent.com/Team-Haruki/haruki-sekai-master/main/master/mysekaiFixtures.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(self.blueprints_map_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
        else:
            raise FileDownloadError("蓝图映射下载失败，若多次重试仍然失败，请使用反馈功能反馈")
    
    def get_weather_map(self) -> None:
        url = f"https://raw.githubusercontent.com/Team-Haruki/haruki-sekai-master/main/master/mysekaiPhenomenas.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(self.weather_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
        else:
            raise FileDownloadError("天气映射下载失败，若多次重试仍然失败，请使用反馈功能反馈")
    
    def get_harvest_info(self) -> None:
        url = f"https://raw.githubusercontent.com/Team-Haruki/haruki-sekai-master/main/master/mysekaiSiteHarvestFixtures.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(self.harvest_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
        else:
            raise FileDownloadError("地图材料信息下载失败，若多次重试仍然失败，请使用反馈功能反馈")
    
    def data_update(self) -> None:
        try:
            self.get_gate_information()
        except FileDownloadError:
            raise
        try:
            self.get_material_map()
        except FileDownloadError:
            raise
        try:
            self.get_blueprints_infomation()
        except FileDownloadError:
            raise
        try:
            self.get_blueprints_map()
        except FileDownloadError:
            raise
        try:
            self.get_weather_map()
        except FileDownloadError:
            raise
        try:
            self.get_harvest_info()
        except FileDownloadError:
            raise

    @staticmethod
    def classify_day(timestamp: int) -> str:
        dt = datetime.fromtimestamp(timestamp)
        date = dt.date()
        time_str = dt.strftime("%H:%M")
        today = datetime.today().date()
        delta = (date - today).days

        if delta == -1:
            return f"昨天{time_str}"
        elif delta == 0:
            return f"今天{time_str}"
        elif delta == 1:
            return f"明天{time_str}"
        else:
            return date.strftime("%Y-%m-%d %H:%M")
    
    def get_mysekai_weather(self, user_id: str) -> dict:
        ms_json_path = self.base_path / "data" / f'user_{user_id}_ms.json'
        with open(ms_json_path, "r", encoding = "utf-8") as f:
            userdata_ms = json.load(f)
        
        with open(self.weather_path, "r", encoding = "utf-8") as f:
            weather_map = json.load(f)
        
        weather_dict = {}
        weather_dict.update({"天气预报": ""})
        for item in userdata_ms["mysekaiPhenomenaSchedules"]:
            t = self.classify_day(int(int(item["scheduleDate"]) / 1000 + (int(item["mysekaiRefreshTimePeriodId"]) - 1) * 43200))
            weather_dict.update({f"{t}": next(weather["name"] for weather in weather_map if weather["id"] == item["mysekaiPhenomenaId"])})
        
        return weather_dict
    
    def get_ms_info(self, user_id: str, user_name: str) -> dict:
        ms_info = {"用户": user_name + "(" + user_id + ")"}
        ms_json_path = self.base_path / "data" / f'user_{user_id}_ms.json'
        with open(ms_json_path, "r", encoding = "utf-8") as f:
            userdata_ms = json.load(f)

        update_time = datetime.fromtimestamp(int(userdata_ms["upload_time"]))
        ms_info.update({"更新时间": update_time})

        ms_info.update(self.get_mysekai_weather(user_id))

        return ms_info

    def get_blurprints_unobtained(self, number: int, user_id: str, user_name: str) -> dict:
        blueprints_unobtained = {"用户": user_name + "(" + user_id + ")"}

        with open(self.blueprints_path, "r", encoding = "utf-8") as f:
            blueprints_map = json.load(f) #蓝图字典

        with open(self.blueprints_map_path, "r", encoding = "utf-8") as f:
            blueprints_fixtures = json.load(f) #家具字典

        ms_json_path = self.base_path / "data" / f'user_{user_id}_ms.json'
        with open(ms_json_path, "r", encoding = "utf-8") as f:
            userdata_ms = json.load(f)

        update_time = datetime.fromtimestamp(int(userdata_ms["upload_time"]))
        now_time = int(datetime.now().timestamp())
        blueprints_unobtained.update({"更新时间": update_time})
        if now_time - int(userdata_ms["upload_time"]) > 86400:
            blueprints_unobtained.update({"数据过期": "请重新上传数据"})
            return blueprints_unobtained
        blueprints_unobtained.update({"蓝图数量": str(len(userdata_ms["updatedResources"]["userMysekaiBlueprints"])) + '/' + str(len(blueprints_map))})

        if len(userdata_ms["updatedResources"]["userMysekaiBlueprints"]) == len(blueprints_map):
            blueprints_unobtained.update({"蓝图已全部获得": len(blueprints_map)})
            return blueprints_unobtained
        else:
            count = number
            obtained_ids = {mi["mysekaiBlueprintId"] for mi in userdata_ms["updatedResources"]["userMysekaiBlueprints"]}
            miss_ids = [bp["id"] for bp in blueprints_map if bp["id"] not in obtained_ids]
            for i in miss_ids[:count]:
                blueprints_unobtained.update({i: next((fixture['name'] for fixture in blueprints_fixtures if fixture['id'] == i), "Name not found")})
            
            blueprints_unobtained.update({f"由于长度限制，显示未获取的前{number}项": ""})
            return blueprints_unobtained

    def get_materials_needed(self, groupid: int, level: int, user_id: str, user_name: str) -> dict:
        materials_needed = {"用户": user_name + "(" + user_id + ")"}

        with open(self.gate_material_path, "r", encoding = "utf-8") as f:
            gate_material_map = json.load(f)

        json_path = self.base_path / "data" / f"user_{user_id}.json"
        with open(json_path, "r", encoding = "utf-8") as f:
            userdata = json.load(f)
        
        update_time = datetime.fromtimestamp(int(userdata["upload_time"]))
        now_time = int(datetime.now().timestamp())
        materials_needed.update({"更新时间": update_time})
        if now_time - int(userdata["upload_time"]) > 86400:
            materials_needed.update({"数据过期": "请重新上传数据"})
            return materials_needed
        materials_needed.update({f"当前{self.get_unit_name(groupid)}等级": userdata["userMysekaiGates"][int(groupid/1000)-1]["mysekaiGateLevel"]})
        if userdata["userMysekaiGates"][int(groupid/1000)-1]["mysekaiGateLevel"] == 40:
            materials_needed.update({"当前团已满级": 40})
            return materials_needed
        elif level <= userdata["userMysekaiGates"][int(groupid/1000)-1]["mysekaiGateLevel"]:
            materials_needed.update({"已达到目标等级": level})
            return materials_needed

        data_to_translate = {}

        for i in range(userdata["userMysekaiGates"][int(groupid/1000)-1]["mysekaiGateLevel"] + 1, level + 1):
            for item in gate_material_map:
                if groupid + i == item["groupId"]:
                    if item["mysekaiMaterialId"] in data_to_translate:
                        data_to_translate[item["mysekaiMaterialId"]] += item["quantity"]
                    else:
                        data_to_translate[item["mysekaiMaterialId"]] = item["quantity"]

        for item in userdata["userMysekaiMaterials"]:
            if item["mysekaiMaterialId"] in data_to_translate:
                data_to_translate[item["mysekaiMaterialId"]] -= item["quantity"]
                if data_to_translate[item["mysekaiMaterialId"]] <= 0:
                    del data_to_translate[item["mysekaiMaterialId"]]

        materials_needed.update(self.data_translate(data_to_translate))
        return materials_needed
    
    def data_translate(self, data: dict) -> dict:
        with open(self.material_path, "r", encoding = "utf-8") as f:
            material_map = json.load(f)
        
        translated_materials_needed = {}
        for materialId, quantity in data.items():
            for item in material_map:
                if materialId == item["id"] and (materialId < 35 or materialId > 60):
                    translated_materials_needed[item["name"]] = quantity
                    break
        
        with open(self.memorial_translate, "r", encoding = "utf-8") as f:
            memorial_map = json.load(f)

        for materialId, quantity in data.items():
            for item in memorial_map["reference"]:
                if materialId == item["id"] and (materialId >= 35 and materialId <= 60):
                    translated_materials_needed[item["name"]] = quantity
                    break

        return translated_materials_needed
    
    def get_harvest_info(self, user_id: str, user_name: str) -> dict:
        harvest_info = {"用户": user_name + "(" + user_id + ")"}

        json_path = self.base_path / "data" / f"user_{user_id}.json"
        with open(json_path, "r", encoding = "utf-8") as f:
            userdata = json.load(f)
        
        with open(self.sub_path, "r", encoding = "utf-8") as f:
            subdata = json.load(f)

        with open(self.harvest_path, "r", encoding = "utf-8") as f:
            harvest_map = json.load(f)
        
        with open(self.material_path, "r", encoding = "utf-8") as f:
            material_map = json.load(f)
        
        update_time = datetime.fromtimestamp(int(userdata["upload_time"]))
        now_time = int(datetime.now().timestamp())
        harvest_info.update({"更新时间": update_time})
        if now_time - int(userdata["upload_time"]) > 86400:
            harvest_info.update({"数据过期": "请重新上传数据"})
            return harvest_info
        
        sub_ids = subdata[user_id]

        for item in userdata["updatedResources"]["userMysekaiHarvestMaps"]:
            map_id = item["mysekaiSiteId"]
            harvest_info.update({f"地图{map_id}": ""})
            material_dict = {}
            for i in sub_ids:
                material_dict.update({i: 0})
            for fixture in item["userMysekaiSiteHarvestResourceDrops"]:
                if fixture["resourceId"] in sub_ids:
                    material_dict[fixture["resourceId"]] += fixture["quantity"]

            flag = False
            for k, v in material_dict.items():
                for item in material_map:
                    if k == item["id"] and (k < 35 or k > 60):
                        if v != 0:
                            harvest_info.update({item["name"]: v})
                            flag = True
            if not flag:
                harvest_info.update({f"地图{map_id}": "没有你想要的材料"})

        return harvest_info

    def get_unit(self, unit: str, user_id: str) -> int:
        ln = ["ln", "leo/need", "blue", "狮雨星绊", "ick", "saki", "hnm", "shiho"]
        mmj = ["mmj", "more more jump", "MORE MORE JUMP!", "green", "萌萌少女飞跃团", "mnr", "hrk", "airi", "szk"]
        vbs = ["vbs", "vivid bad squad", "Vivid BAD SQUAD", "red", "炫狂小队", "khn", "an", "akt", "toya"]
        ws = ["ws", "Wonderlands showtime", "yellow", "马戏团", "tks", "emu", "nene", "rui"]
        nigo = ["25", "nigo", "25h", "purple", "25时", "knd", "mfy", "ena", "mzk"]

        if not unit:
            json_path = self.base_path / "data" / f"user_{user_id}.json"
            with open(json_path, "r", encoding = "utf-8") as f:
                userdata = json.load(f)
            for item in userdata["userMysekaiGates"]:
                if item["isSettingAtHomeSite"]:
                    return int(item["mysekaiGateId"] * 1000)
        if unit in ln:
            return 1000
        elif unit in mmj:
            return 2000
        elif unit in vbs:
            return 3000
        elif unit in ws:
            return 4000
        elif unit in nigo:
            return 5000
        else:
            raise NotFoundError("不存在的团体或关联团体名称")
    
    def get_unit_name(self, unit: int) -> str:
        if unit == 1000:
            return "ln"
        elif unit == 2000:
            return "mmj"
        elif unit == 3000:
            return "vbs"
        elif unit == 4000:
            return "ws"
        elif unit == 5000:
            return "25"
    
    def generate_card_pic(self, user_id: str) -> str:
        json_path = self.base_path / "data" / f"user_{user_id}.json"
        with open(json_path, "r", encoding = "utf-8") as f:
            userdata = json.load(f)
        
        image = Image.new("RGB", (1280, 720), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        font_path = self.base_path / "src" / "font" / "SOURCEHANSANSCN-REGULAR.OTF"
        font = ImageFont.truetype(font_path, 40)

        update_time = datetime.fromtimestamp(int(userdata["upload_time"]))
        test_text = f"更新时间: {update_time}"
        draw.text((20, 20), test_text, fill=(0, 0, 0), font=font)

        card_info_pic_path = self.base_path / "userdata" / f"card_info_{user_id}.png"
        image.save(card_info_pic_path)
        return str(card_info_pic_path)