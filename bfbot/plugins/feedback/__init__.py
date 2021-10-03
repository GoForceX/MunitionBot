import nonebot
from nonebot import on_command, logger
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import traceback

feedback = on_command("feedback")


@feedback.handle()
async def handle_message(bot: Bot, event: Event, state: T_State):
    sender_id = event.get_user_id()
    msg = str(event.get_message()).strip()
    try:
        for user in nonebot.get_driver().config.superusers:
            await bot.send_private_msg(user_id=user, message=f'用户{sender_id}给bot提了个小建议哦' + '\n' + msg)
    except Exception as e:
        logger.error(traceback.format_exc())
        await feedback.finish('呜呜呜发送失败了，请稍后再试试')
    await feedback.finish('已经传达到管理员啦~')
