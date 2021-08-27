from nonebot import on_request
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.event import FriendRequestEvent, GroupRequestEvent
from nonebot.log import logger

async def on_friend_request(bot: Bot, event: Event, state: T_State) -> bool: 
    return isinstance(event, FriendRequestEvent)

async def on_group_request(bot: Bot, event: Event, state: T_State) -> bool: 
    return isinstance(event, GroupRequestEvent)

friend_req = on_request(on_friend_request)
group_req = on_request(on_group_request)

@friend_req.handle()
async def accept_friend_request(bot: Bot, event: Event, state: T_State) -> bool:
    await event.approve(bot)

@group_req.handle()
async def accept_group_request(bot: Bot, event: Event, state: T_State) -> bool:
    if event.sub_type == 'invite':
        await event.approve(bot)