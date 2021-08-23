from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import httpx, os, base64
from nonebot.log import logger
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from nonebot.adapters.cqhttp.message import MessageSegment
from nonebot.adapters import Message

query = on_command("player") 

@query.handle()
async def handle_message(bot: Bot, event: Event, state: T_State):
    sender_id = event.get_user_id()
    message_type = event.get_session_id().split('_')[0]
    args = str(event.get_message()).strip().split(' ')
    if len(args) == 1:
        await query.finish("呀，版本号或者ID不见了呢（笑")
    if len(args) != 2:
        await query.finish("命令格式突然不对劲起来了（笑\n格式是#player <bf1/bf4/bfv> <id>哦")
    if args[0] == "bf1" or args[0] == "bf4" or args[0] == "bfv":
        if args[0] and args[1]:
            logger.debug("Requesting: https://api.gametools.network/" + args[0] + "/stats/?name=" + args[1] + "&lang=zh-cn")
            async with httpx.AsyncClient() as client:
                try:
                    await query.send("稍等下，正在获取您请求的信息……")
                    resp = await client.get("https://api.gametools.network/" + args[0] + "/stats/?name=" + args[1] + "&lang=zh-cn", timeout=5.0)
                except httpx.ReadTimeout:
                    await query.finish("太对不起了，请求超时了（悲")
                result = resp.json()
                logger.debug(result)
                if "detail" in result:
                    await query.finish("欸，找不到此ID对应的玩家")
                text = ("用户名：" +
                str(result["userName"]) +
                "\n等级：" +
                str(result["rank"]) +
                "\n命中率：" +
                str(result["accuracy"]) +
                "\n爆头率：" +
                str(result["headshots"]) +
                "\nK/D：" +
                str(result["killDeath"]) +
                "\nKPM：" +
                str(result["killsPerMinute"]) +
                "\n协助击杀数：" +
                str(result["killAssists"]) +
                "\nK：" +
                str(result["kills"]) +
                "\nD：" +
                str(result["deaths"]) +
                "\nWin：" +
                str(result["wins"]) +
                "\nLose：" +
                str(result["loses"]) +
                "\n胜率：" +
                str(result["winPercent"]))

                image = Image.open(os.path.join(os.path.abspath('.'), 'bf-mod.png'))
                drawer = ImageDraw.Draw(image)
                font = ImageFont.truetype(os.path.join(os.path.abspath('.'), 'DENG.TTF'), 40)
                drawer.text((50, 50), text, font=font, fill="#000090")
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