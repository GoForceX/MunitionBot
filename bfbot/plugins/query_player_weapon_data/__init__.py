from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event, Message
from nonebot.adapters.cqhttp.message import MessageSegment
from nonebot.log import logger
import httpx
import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

query = on_command("weapon")


@query.handle()
async def handle_message(bot: Bot, event: Event, state: T_State):
    sender_id = event.get_user_id()
    args = str(event.get_message()).strip().split(' ')
    if len(args) == 1:
        await query.finish("呀，版本号或者ID不见了呢（笑")
    if len(args) != 2:
        await query.finish("命令格式突然不对劲起来了（笑\n格式是#weapon <bf1/bfv> <name>哦")
    if args[0] == "bf1" or args[0] == "bfv":
        if args[0] and args[1]:
            logger.debug(
                "Requesting: https://api.gametools.network/" + args[0] + "/weapons/?name=" + args[1] + "&lang=" + (
                    "zh-cn" if args[0] == 'bfv' else "zh-tw"))
            async with httpx.AsyncClient() as client:
                try:
                    await query.send("稍等下，正在获取您请求的信息……")
                    resp = await client.get(
                        "https://api.gametools.network/" + args[0] + "/weapons/?name=" + args[1] + "&lang=" + (
                            "zh-cn" if args[0] == 'bfv' else "zh-tw"), timeout=10.0)
                except httpx.ReadTimeout:
                    await query.finish("太对不起了，请求超时了（悲")
                result = resp.json()["weapons"]
                logger.debug(result)
                if "detail" in result:
                    await query.finish("欸，找不到此ID对应的玩家")
                result = sorted(result, key=lambda x: x['kills'], reverse=True)

                image = Image.open(os.path.join(os.path.abspath('.'), 'static', f'{args[0]}-top8.png'))
                drawer = ImageDraw.Draw(image)
                font = ImageFont.truetype(
                    os.path.join(
                        os.path.abspath('.'),
                        'static',
                        'HarmonyOS_Sans_SC_Regular.ttf'
                    ), 20)
                for i in range(4):
                    for j in range(2):
                        drawer.text((83 + 416 * j, 40 + 163 * i),
                                    f'{result[2 * i + j]["weaponName"]}' + '\n' + f'击杀:{result[2 * i + j]["kills"]}'.ljust(
                                        14) + f'爆头:{int(result[2 * i + j]["kills"] * float(result[2 * i + j]["headshots"][:-1]) / 100)}'.center(
                                        14) + '\n' + f'命中率:{result[2 * i + j]["accuracy"]}'.ljust(
                                        14) + f'爆头率:{result[2 * i + j]["headshots"]}'.center(
                                        14) + '\n' + f'效率:{result[2 * i + j]["hitVKills"]}'.ljust(
                                        14) + f'KPM:{result[2 * i + j]["killsPerMinute"]}'.center(14), font=font,
                                    fill="#e0e0e0")

                img_io = BytesIO()
                image.save(img_io, format="PNG")

                await query.finish(
                    Message(
                        (MessageSegment.at(sender_id) if event.get_session_id().startswith('group') else '') +
                        MessageSegment.image("base64://" + base64.b64encode(img_io.getvalue()).decode())
                    )
                )
        await query.finish("怪起来了，你这指令有问题啊")
    await query.finish("版本只能是bf1/bfv，别搞错了哦（顺带一提这个暂时还不支持bf4")
