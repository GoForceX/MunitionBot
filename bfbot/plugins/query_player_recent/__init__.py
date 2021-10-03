from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import httpx, os, base64, datetime
from nonebot.log import logger
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from nonebot.adapters.cqhttp.message import MessageSegment
from nonebot.adapters import Message

query = on_command("recent") 

bfv_maps = {
    "MP_Jungle": "所罗门群岛",
    "MP_Halfaya": "岩漠",
    "MP_Hannut_US": "战车风暴", 
    "MP_SandAndSea": "艾尔舒丹", 
    "MP_Foxhunt": "小型机场", 
    "MP_TropicIslands": "太平洋风暴", 
    "MP_Escaut": "扭曲钢铁", 
    "MP_Arras": "阿拉斯", 
    "MP_Devastation": "荒废之地", 
    "MP_IwoJima": "硫磺岛",
    "MP_Bunker": "地下行动", 
    "MP_ArcticFjord": "纳尔维克", 
    "MP_Kalamas": "马瑞塔", 
    "MP_Crete": "水星", 
    "MP_WakeIsland": "威客岛", 
    "MP_ArcticFjell": "菲耶尔652", 
    "MP_Norway": "罗弗敦群岛", 
    "MP_Provence": "普罗旺斯",
    "MP_Rotterdam": "鹿特丹",
    "MP_Libya":"迈尔季营地"
}

bfv_modes = {
    "Breakthrough0":"突破",
    "Conquest0":"征服"
}

@query.handle()
async def handle_message(bot: Bot, event: Event, state: T_State):
    sender_id = event.get_user_id()
    args = str(event.get_message()).strip().split(' ')
    if len(args) == 1:
        await query.finish("呀，版本号或者ID不见了呢（笑")
    if len(args) != 2:
        await query.finish("命令格式突然不对劲起来了（笑\n格式是#recent <bfv> <name>哦")
    if args[0] == "bfv":
        if args[0] and args[1]:
            logger.debug("Requesting: https://api.tracker.gg/api/v1/" + args[0] + "gamereports/origin/latest/" + args[1])
            async with httpx.AsyncClient() as client:
                try:
                    await query.send("稍等下，正在获取您请求的信息……")
                    resp = await client.get("https://api.tracker.gg/api/v1/" + args[0] + "/gamereports/origin/latest/" + args[1], timeout=10.0)
                except httpx.ReadTimeout:
                    await query.finish("太对不起了，请求超时了（悲")
                result = resp.json()["data"]["reports"]
                logger.debug(result)
                if "errors" in result:
                    await query.finish("欸，找不到此ID对应的玩家")
                image = Image.open(os.path.join(os.path.abspath('.'), 'static', f'{args[0]}-top8.png'))
                drawer = ImageDraw.Draw(image)
                font = ImageFont.truetype(os.path.join(os.path.abspath('.'), 'static', 'HarmonyOS_Sans_SC_Regular.ttf'), 20)
                for i in range(4): 
                    for j in range(2):
                        if 2*i+j >= len(result):
                            break
                        playTime = datetime.datetime.utcfromtimestamp(result[2*i+j]["timestamp"])
                        strTime = playTime.strftime("%Y-%m-%d %H:%M:%S")
                        drawer.text((83 + 416 * j, 40 + 163 * i),  "服务器名：" +
                            str(result[2*i+j]["serverName"][:22] + ('...' if len(result[2*i+j]["serverName"]) > 22 else '')) +
                            ("\n模式：" +
                            str(bfv_modes[result[2*i+j]["modeKey"]])).ljust(10) +
                            ("地图：" +
                            str(bfv_maps[result[2*i+j]["mapKey"]])).center(14) +
                            ("\n游玩时间：\n" + strTime), font=font, fill="#e0e0e0")

                img_io = BytesIO()
                image.save(img_io, format="PNG")
                
                await query.finish(
                    Message(
                        (MessageSegment.at(sender_id) if event.get_session_id().startswith('group') else '') +
                        MessageSegment.image("base64://" + base64.b64encode(img_io.getvalue()).decode())
                    )
                )
        await query.finish("怪起来了，你这指令有问题啊")
    await query.finish("版本只能是bfv，别搞错了哦（顺带一提这个暂时还不支持bf1/4")