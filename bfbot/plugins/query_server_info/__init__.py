import base64
from io import BytesIO
import os
from PIL import Image, ImageDraw, ImageFont
from nonebot import on_command
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import httpx
from nonebot.log import logger

query = on_command("server") 

@query.handle()
async def handle_message(bot: Bot, event: Event, state: T_State):
    sender_id = event.get_user_id()
    args = str(event.get_message()).strip().split(' ')
    if len(args) == 1:
        await query.finish("呀，版本号或者服务器名不见了呢（笑")
    if len(args) != 2:
        await query.finish("命令格式突然不对劲起来了（笑\n格式是#server <bf1/bf4/bfv> <name>哦")
    if args[0] == "bf1" or args[0] == "bf4" or args[0] == "bfv":
        if args[0] and args[1]:
            logger.debug("Requesting: https://api.gametools.network/" + args[0] + "/servers/?name=" + args[1] + "&lang=" + ("zh-cn" if args[0] == 'bfv' else "zh-tw") + "&region=all&platform=pc&limit=8")
            async with httpx.AsyncClient() as client:
                try:
                    await query.send("稍等下，正在获取您请求的信息……")
                    resp = await client.get("https://api.gametools.network/" + args[0] + "/servers/?name=" + args[1] + "&lang=" + ("zh-cn" if args[0] == 'bfv' else "zh-tw") + "&region=all&platform=pc&limit=8", timeout=10.0)
                except httpx.ReadTimeout:
                    await query.finish("太对不起了，请求超时了（悲")
                result = resp.json()["servers"]
                logger.debug(result)
                if len(result) == 0:
                    await query.finish("欸，找不到此名称对应的服务器")
                image = Image.open(os.path.join(os.path.abspath('.'), 'static', f'{args[0]}-top8.png'))
                drawer = ImageDraw.Draw(image)
                font = ImageFont.truetype(os.path.join(os.path.abspath('.'), 'static', 'HarmonyOS_Sans_SC_Regular.ttf'), 20)
                for i in range(4): 
                    for j in range(2):
                        if 2*i+j >= len(result):
                            break
                        drawer.text((83 + 416 * j, 40 + 163 * i),  "服务器名：" +
                            str(result[2*i+j]["prefix"][:22] + ('...' if len(result[2*i+j]["prefix"]) > 22 else '')) +
                            "\n状态：" +
                            str(result[2*i+j]["serverInfo"]) +
                            " [" +
                            str(result[2*i+j]["inQue"]) +
                            "]" +
                            ("\n模式：" +
                            str(result[2*i+j]["mode"])).ljust(10) +
                            ("地图：" +
                            str(result[2*i+j]["currentMap"])).center(14) +
                            ("\n区服：" +
                            str(result[2*i+j]["region"])).ljust(14) +
                            ("平台：" +
                            str(result[2*i+j]["platform"])).center(14), font=font, fill="#e0e0e0")
                
                img_io = BytesIO()
                image.save(img_io, format="PNG")
                
                await query.finish(
                    Message(
                        MessageSegment.at(sender_id) + 
                        MessageSegment.image("base64://" + base64.b64encode(img_io.getvalue()).decode())
                    )
                )
        await query.finish("怪起来了，你这指令有问题啊")
    await query.finish("版本只能是bf1/bf4/bfv，别搞错了哦")