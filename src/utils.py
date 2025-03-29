from pathlib import Path
import json
import requests
from .exception import error_status as s
from datetime import datetime

class Utils:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.bond_path = self.base_path / "userdata" / "bond.json"
        self.gate_material_path = self.base_path / "data" / "mysekaiGateMaterialGroups.json"
        self.material_path = self.base_path / "data" / "mysekaiMaterials.json"
        self.memorial_translate = self.base_path / "data" / "reference.json"
    
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
    
    def get_user_data(self, user_id: str) -> s:

        with open(self.bond_path, "r", encoding = "utf-8") as f:
            data = json.load(f)
        found = False
        for item in data:
            if user_id in item:
                uid = item[user_id]
                found = True
                break

        if not found:
            return s("用户未绑定", -1)
        
        json_path = self.base_path / "data" / f"user_{user_id}.json"
        url = f"api" # configure it if you need

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(json_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
            return s("用户信息下载成功", 1)
        else:
            return s("用户信息下载失败", -2)
    
    def get_gate_information(self) -> s:
        url = f"https://raw.githubusercontent.com/Team-Haruki/haruki-sekai-master/main/master/mysekaiGateMaterialGroups.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(self.gate_material_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
            return s("升级材料下载成功", 1)
        else:
            return s("升级材料下载失败", -2)
        
    def get_material_map(self) -> s:
        url = f"https://raw.githubusercontent.com/Team-Haruki/haruki-sekai-master/main/master/mysekaiMaterials.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(self.material_path, "w", encoding = "utf-8") as f:
                json.dump(data, f, indent = 4)
            return s("材料映射下载成功", 1)
        else:
            return s("材料映射下载失败", -2)
    
    def data_update(self) -> s:
        status1 = self.get_gate_information()
        status2 = self.get_material_map()
        if status1.code == 1 and status2.code == 1:
            return s("数据更新成功", 1)
        elif status1.code == -2:
            return s(status1.message, -1)
        elif status2.code == -2:
            return s(status2.message, -1)
    
    def get_materials_needed(self, groupid: int, level: int, user_id: str) -> dict:
        materials_needed = {"用户": user_id}

        with open(self.gate_material_path, "r", encoding = "utf-8") as f:
            gate_material_map = json.load(f)

        json_path = self.base_path / "data" / f"user_{user_id}.json"
        with open(json_path, "r", encoding = "utf-8") as f:
            userdata = json.load(f)
        
        update_time = datetime.fromtimestamp(int(userdata["upload_time"]))
        materials_needed.update({"更新时间": update_time})
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
            return -1
    
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