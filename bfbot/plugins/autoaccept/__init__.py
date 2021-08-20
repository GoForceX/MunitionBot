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


from nonebot import on_request
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.mirai.event.request import NewFriendRequestEvent, BotInvitedJoinGroupRequestEvent
from nonebot.log import logger

async def on_friend_request(bot: Bot, event: Event, state: T_State) -> bool: 
    return isinstance(event, NewFriendRequestEvent)

async def on_group_request(bot: Bot, event: Event, state: T_State) -> bool: 
    return isinstance(event, BotInvitedJoinGroupRequestEvent)

friend_req = on_request(on_friend_request)
group_req = on_request(on_group_request)

@friend_req.handle()
@group_req.handle()
async def accept_request(bot: Bot, event: Event, state: T_State) -> bool:
    await event.approve(bot)