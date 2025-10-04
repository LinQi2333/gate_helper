from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent
from nonebot.params import ArgPlainText, CommandArg
from src.utils import Utils
from src.cn_module import CNModule

utils = Utils()
cnmodule = CNModule()

bond = on_command("bond", aliases = {"绑定"}, priority = 5)
cnbond = on_command("cnbond", aliases = {"cn绑定"}, priority = 5)
cnms = on_command("cnms", aliases = {"cnmsa"}, priority = 5)
gate_material = on_command("gate_material", aliases = {"升级材料", "msg"}, priority = 5)
blueprint_obt = on_command("mysekai_blueprint", aliases = {"蓝图获取情况", "msbp"}, priority = 5)
sub_material = on_command("sub_material", aliases = {"查询订阅", "msub"}, priority = 5)
sub_bond = on_command("sub_bond", aliases = {"订阅", "subscribe"}, priority = 5)
ms_info = on_command("ms_info", aliases = {"ms信息", "msi"}, priority = 5)
update = on_command("update", aliases = {"更新ms数据"}, priority = 5)
card_info = on_command("card_info", aliases = {"个人图鉴"}, priority = 5)

@bond.handle()
async def bond_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    uid = args.extract_plain_text()
    user_id = str(event.user_id)
    utils.bond_user(user_id, uid)
    await bond.finish("绑定成功！")

@cnbond.handle()
async def cnbond_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    uid = args.extract_plain_text()
    user_id = str(event.user_id)
    cnmodule.bond_user(user_id, uid)
    await cnbond.finish("cn绑定成功！")

@cnms.handle()
async def cnms_handle(bot: Bot, event: GroupMessageEvent):
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    try:
        utils.get_user_data(user_id)
    except Exception as e:
        await cnms.finish(e.message)
    
    user_info = await bot.get_group_member_info(group_id=group_id, user_id=int(user_id))
    user_name = user_info.get("card") or user_info.get("nickname")
    material = cnmodule.get_harvest_info(user_id, user_name)
    messages = ""
    for item in material:
        for k, v in item.items():
            messages = messages + str(k) + ":" + str(v) + "\n"
    await cnms.finish(messages)

@gate_material.handle()
async def gate_material_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args_in = args.extract_plain_text()
    unit, _, level = args_in.partition(" ")
    user_id = str(event.user_id)
    group_id = str(event.group_id)

    try:
        utils.get_user_data(user_id)
    except Exception as e:
        await gate_material.finish(e.message)

    try:
        groupid = utils.get_unit(unit, user_id)
    except Exception as e:
        await gate_material.finish(e.message)

    if not level:
        level = 40
    elif int(level) < 0 or int(level) > 40:
        await gate_material.finish("指定的等级不存在")
    else:
        target_level = int(level)
    
    if utils.gate_material_path.exists() and utils.material_path.exists():
        user_info = await bot.get_group_member_info(group_id=group_id, user_id=int(user_id))
        user_name = user_info.get("card") or user_info.get("nickname")
        materials = utils.get_materials_needed(groupid, target_level, user_id, user_name)
    
    messages = ""
    for material_needed, quantity in materials.items():
        if material_needed == "当前团已满级✨":
            messages = messages + material_needed + "\n"
        elif material_needed == "已达到目标等级":
            messages = messages + material_needed + "\n"
        else:
            messages = messages + material_needed + ":" + str(quantity) + "\n"
    await gate_material.finish(messages)

@blueprint_obt.handle()
async def blueprint_obt_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args_in = args.extract_plain_text()

    user_id = str(event.user_id)
    group_id = str(event.group_id)

    if not args_in:
        number = 10
    elif int(args_in) >20:
        number = 20
        await bot.send_group_msg(group_id = event.group_id, message = "显示数量过大，已限制为20")
    elif int(args_in) < 1:
        number = 10
        await bot.send_group_msg(group_id = event.group_id, message = "查询数量过小，采用默认查询数量")
    else:
        number = int(args_in)

    try:
        utils.get_user_ms_data(user_id)
    except Exception as e:
        await blueprint_obt.finish(e.message)

    if utils.blueprints_path.exists() and utils.blueprints_map_path.exists():
        user_info = await bot.get_group_member_info(group_id=group_id, user_id=int(user_id))
        user_name = user_info.get("card") or user_info.get("nickname")
        blueprints = utils.get_blueprints_unobtained(number, user_id, user_name)

    messages = ""
    dict_length = len(blueprints)
    
    for i, (blueprint, name) in enumerate(blueprints.items()):
        if i == dict_length - 1:
            messages = messages + str(blueprint) + str(name)
        else:
            messages = messages + str(blueprint) + ":" + str(name) + "\n"
    await blueprint_obt.finish(messages)

@sub_bond.handle()
async def sub_bond_handle(bot: Bot, event: GroupMessageEvent):
    messages = "请发送你需要订阅的材料id，以空格分割\n材料id列表如下图\n"
    messages = messages + "[CQ:image,file=file:///home/ubuntu/bot/rin/rin/plugins/gate_helper/userdata/material_id.png]"
    await bot.send_group_msg(group_id = event.group_id, message = messages)

@sub_bond.got("subs")
async def sub_bond_got_handle(bot: Bot, event: GroupMessageEvent, subs: str = ArgPlainText("subs")):
    user_id = str(event.user_id)

    sub_list = list(map(int, subs.split()))
    utils.bond_sub(user_id, sub_list)
    await sub_bond.finish("订阅成功！")

@sub_material.handle()
async def sub_material_handle(bot: Bot, event: GroupMessageEvent):
    user_id = str(event.user_id)
    group_id = str(event.group_id)

    try:
        utils.get_user_ms_data(user_id)
    except Exception as e:
        await sub_material.finish(e.message)
    try:
        utils.get_user_sub(user_id)
    except Exception as e:
        await sub_material.finish(e.message)
            
    user_info = await bot.get_group_member_info(group_id=group_id, user_id=int(user_id))
    user_name = user_info.get("card") or user_info.get("nickname")
    harvest = utils.get_harvest_info(user_id, user_name)

    messages = ""
    for item in harvest:
        for k, v in item.items():
            messages = messages + str(k) + ":" + str(v) + "\n"
    await sub_material.finish(messages)

@ms_info.handle()
async def ms_info_handle(bot: Bot, event: GroupMessageEvent):
    user_id = str(event.user_id)
    group_id = str(event.group_id)

    try:
        utils.get_user_ms_data(user_id)
    except Exception as e:
        await ms_info.finish(e.message)
    
    if utils.weather_path.exists():
        user_info = await bot.get_group_member_info(group_id=group_id, user_id=int(user_id))
        user_name = user_info.get("card") or user_info.get("nickname")
        mysekai_info = utils.get_ms_info(user_id, user_name)
    
    messages = ""
    for key, value in mysekai_info.items():
        messages = messages + str(key) + ":" + str(value) + "\n"
    await ms_info.finish(messages)

@update.handle()
async def update_handle(bot: Bot, event: GroupMessageEvent):
    try:
        utils.data_update()
    except Exception as e:
        await update.finish(e.message)
    else:
        await update.finish("更新成功！")
    
@card_info.handle()
async def card_info_handle(bot: Bot, event: GroupMessageEvent):
    user_id = str(event.user_id)

    try:
        utils.get_user_data(user_id)
    except Exception as e:
        await card_info.finish(e.message)

    pic_path = utils.generate_card_pic(user_id)
    msg = f"[CQ:image,file=file:///{pic_path}]"
    await bot.send_group_msg(group_id = event.group_id, message = msg)