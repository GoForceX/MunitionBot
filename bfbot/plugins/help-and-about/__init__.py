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
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.log import logger

help = on_command("help") 

@help.handle()
async def help_handler(bot: Bot, event: Event, state: T_State):
    await help.finish("""指令帮助
==============
#player <bf1/bf4/bfv> <id>
查询某玩家的基本信息
#server <bf1/bf4/bfv> <name>
根据服务器名字查找服务器
#help
展示此帮助
#about
显示bot信息""")


about = on_command("about") 

@about.handle()
async def about_handler(bot: Bot, event: Event, state: T_State):
    await about.finish("""关于此Bot
版本：0.1.0 beta 1 (2021.08.20)

bot目前仍处在BETA阶段，可能会出现一些bug，请您多多谅解。

此Bot基于mirai[https://github.com/mamoe/mirai]
与nonebot[https://github.com/nonebot/nonebot2]
两个项目进行开发，并使用了由[https://gametools.network]提供的api，
开发者对以上项目表示感谢。
此Bot基于AGPL 3.0协议开源[https://github.com/GoForceX/BFBot/]。

战地系列游戏是由EA与DICE工作室制作并发行的，
本工具与EA或DICE工作室无关。""")

status = on_command("status", permission=SUPERUSER)

@status.handle()
async def status_handler(bot: Bot, event: Event, state: T_State):
    await status.finish("BOT目前在线")