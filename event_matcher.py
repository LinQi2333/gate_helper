from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent
from nonebot.params import CommandArg
from src.utils import Utils

utils = Utils()

bond = on_command("bond", aliases = {"绑定"}, priority = 5)
gate_material = on_command("gate_material", aliases = {"升级材料"}, priority = 5)
update = on_command("update", aliases = {"更新ms数据"}, priority = 5)
card_info = on_command("card_info", aliases = {"个人图鉴"}, priority = 5)

@bond.handle()
async def bond_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    uid = args.extract_plain_text()
    qq = str(event.user_id)
    utils.bond_user(qq, uid)
    await bond.finish("绑定成功！")

@gate_material.handle()
async def gate_material_handle(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    args_in = args.extract_plain_text()
    unit, _, level = args_in.partition(" ")
    user_id = str(event.user_id)

    user_data_status = utils.get_user_data(user_id)
    if(user_data_status.code != 1):
        await gate_material.finish(user_data_status.message)

    groupid = utils.get_unit(unit, user_id)
    if groupid == -1:
        await gate_material.finish("不存在的团体")
    elif groupid == -2:
        await gate_material.finish("你已经全部满级✨")
    if not level:
        level = 40
    elif int(level) < 0 or int(level) > 40:
        await gate_material.finish("指定的等级不存在")
    else:
        target_level = int(level)
    
    if utils.gate_material_path.exists() and utils.material_path.exists():
        materials = utils.get_materials_needed(groupid, target_level, user_id)
    
    messages = ""
    for material_needed, quantity in materials.items():
        if material_needed == "当前团已满级✨":
            messages = messages + material_needed + "\n"
        elif material_needed == "已达到目标等级":
            messages = messages + material_needed + "\n"
        else:
            messages = messages + material_needed + ":" + str(quantity) + "\n"
    await gate_material.finish(messages)

@update.handle()
async def update_handle(bot: Bot, event: GroupMessageEvent):
    status = utils.data_update()
    if status.code == 1:
        await update.finish("更新成功！")
    elif status.code == -1:
        await update.finish(status.message)
    
@card_info.handle()
async def card_info_handle(bot: Bot, event: GroupMessageEvent):
    user_id = str(event.user_id)

    user_data_status = utils.get_user_data(user_id)
    if(user_data_status.code!= 1):
        await card_info.finish(user_data_status.message)

    pic_path = utils.generate_card_pic(user_id)
    msg = f"[CQ:image,file=file:///{pic_path}]"
    await bot.send_group_msg(group_id = event.group_id, message = msg)