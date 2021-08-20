from pathlib import Path

import nonebot
from nonebot import get_driver

from .config import Config

global_config = get_driver().config
config = Config(**global_config.dict())

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "plugins").
    resolve()))

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import httpx
from nonebot.log import logger

query = on_command("player") 

@query.handle()
async def handle_message(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(' ')
    if len(args) == 1:
        await query.finish("呀，版本号或者ID不见了呢（笑")
    if len(args) != 2:
        await query.finish("命令格式突然不对劲起来了（笑\n格式是#player <bf1/bf4/bfv> <id>哦")
    if args[0] == "bf1" or args[0] == "bf4" or args[0] == "bfv":
        if args[0] and args[1]:
            logger.debug("Requesting: https://api.gametools.network/" + args[0] + "/stats/?name=" + args[1] + "&lang=en-us")
            async with httpx.AsyncClient() as client:
                try:
                    await query.send("稍等下，正在获取您请求的信息……")
                    resp = await client.get("https://api.gametools.network/" + args[0] + "/stats/?name=" + args[1] + "&lang=en-us", timeout=5.0)
                except httpx.ReadTimeout:
                    await query.finish("太对不起了，请求超时了（悲")
                result = resp.json()
                logger.debug(result)
                if "detail" in result:
                    await query.finish("欸，找不到此ID对应的玩家")
                await query.finish("用户名：" +
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
        await query.finish("怪起来了，你这指令有问题啊")
    await query.finish("版本只能是bf1/bf4/bfv，别搞错了哦")