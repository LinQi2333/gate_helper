from pathlib import Path
import json
from .exception import FileDownloadError, UserError, NotFoundError
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class CNModule:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.bond_path = self.base_path / "userdata" / "cnbond.json"

        self.material_path = self.base_path / "data" / "mysekaiMaterials.json"

        self.memorial_translate = self.base_path / "data" / "reference.json"
    
    def bond_user(self, user_id: str, uid: str)-> None:
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
        
        json_path = self.base_path / "data" / f"user_{user_id}_ms.json"

        if not json_path.exists():
            raise FileDownloadError("未找到用户数据")
    
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
    
    def get_harvest_info(self, user_id: str, user_name: str) -> list:
        result = []
        harvest_info = {"用户": user_name + "(" + user_id + ")"}

        json_path = self.base_path / "data" / f"user_{user_id}_ms.json"
        with open(json_path, "r", encoding = "utf-8") as f:
            userdata = json.load(f)
        
        with open(self.material_path, "r", encoding = "utf-8") as f:
            material_map = json.load(f)
        
        # update_time = datetime.fromtimestamp(int(userdata["upload_time"]))
        # now_time = int(datetime.now().timestamp())
        # harvest_info.update({"更新时间": update_time})
        
        # if now_time - int(userdata["upload_time"]) > 86400:
        #     harvest_info.update({"数据过期": "请重新上传数据"})
        #     result.append(harvest_info)
        #     return result
        
        result.append(harvest_info)
        
        # for item in subdata:
        #     if user_id in item:
        #         sub_ids = item[user_id]

        for item in userdata["updatedResources"]["userMysekaiHarvestMaps"]:
            material_info = {}
            map_id = item["mysekaiSiteId"]
            if map_id == 5:
                map_name = "さいしょの原っぱ"
            elif map_id == 6:
                map_name = "願いの砂浜"
            elif map_id == 7:
                map_name = "彩りの花畑"
            elif map_id == 8:
                map_name = "忘れ去られた場所"
            material_info.update({f"图{map_id - 4}：{map_name}": ""})
            material_dict = {}
            for fixture in item["userMysekaiSiteHarvestResourceDrops"]:
                rid = fixture["resourceId"]
                qty = fixture["quantity"]

                material_dict[rid] = material_dict.get(rid, 0) + qty
                # material_dict[fixture["resourceId"]] += fixture["quantity"]
            
            for k, v in material_dict.items():
                for item in material_map:
                    if k == item["id"] and (k < 35 or k > 60):
                        if v != 0:
                            material_info.update({item["name"]: v})
            result.append(material_info)
                                        
        return result