import base64
from io import BytesIO
import os
from PIL import Image
from nonebot import on_command
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

help_matcher = on_command("help")


@help_matcher.handle()
async def help_handler(bot: Bot, event: Event, state: T_State):
    sender_id = event.get_user_id()
    msg = """指令帮助
    ==============
    #player <bf1/bf4/bfv> <id>
    查询某玩家的基本信息
    #server <bf1/bf4/bfv> <name>
    根据服务器名字查找服务器
    #weapon <bf1/bfv> <id>
    根据玩家ID查找玩家战绩较突出的武器
    #recent <bfv> <name>
    根据玩家ID查询最近游玩信息
    #trans <origin-lang> <dest-lang> <msg>
    将您所给的文字翻译成其他语言（源语言可设置为Auto）
    #feedback <msg>
    给bot提建议
    #help
    展示此帮助
    #about
    显示bot信息"""
    if event.get_session_id().startswith('group'):
        await bot.send_private_msg(user_id=sender_id, message=msg)
        await help_matcher.finish("为防止刷屏，已经发送至您的私聊。")
    else:
        await help_matcher.finish(msg)


about = on_command("about")


@about.handle()
async def about_handler(bot: Bot, event: Event, state: T_State):
    image = Image.open(os.path.join('static', 'about_banner.png'))
    img_io = BytesIO()
    image.save(img_io, format="PNG")

    await about.finish(Message(
        '版本: 0.8.0-beta.1+20211003' +
        MessageSegment.image("base64://" + base64.b64encode(img_io.getvalue()).decode())
    ))


status = on_command("status", permission=SUPERUSER)


@status.handle()
async def status_handler(bot: Bot, event: Event, state: T_State):
    await status.finish("BOT目前在线")
