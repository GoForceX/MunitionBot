from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import httpx
from nonebot.log import logger

query = on_command("server") 

@query.handle()
async def handle_message(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(' ')
    if len(args) == 1:
        await query.finish("呀，版本号或者服务器名不见了呢（笑")
    if len(args) != 2:
        await query.finish("命令格式突然不对劲起来了（笑\n格式是#server <bf1/bf4/bfv> <name>哦")
    if args[0] == "bf1" or args[0] == "bf4" or args[0] == "bfv":
        if args[0] and args[1]:
            logger.debug("Requesting: https://api.gametools.network/" + args[0] + "/servers/?name=" + args[1] + "&lang=zh-cn&region=all&platform=pc&limit=10")
            async with httpx.AsyncClient() as client:
                try:
                    await query.send("稍等下，正在获取您请求的信息……")
                    resp = await client.get("https://api.gametools.network/" + args[0] + "/servers/?name=" + args[1] + "&lang=zh-cn&region=all&platform=pc&limit=10", timeout=10.0)
                except httpx.ReadTimeout:
                    await query.finish("太对不起了，请求超时了（悲")
                result = resp.json()["servers"]
                logger.debug(result)
                if len(result) == 0:
                    await query.finish("欸，找不到此名称对应的服务器")
                results = []
                for i in result:
                    results.append("服务器名：" +
                        str(i["prefix"]) +
                        "\n状态：" +
                        str(i["serverInfo"]) +
                        "[" +
                        str(i["inQue"]) +
                        "]" +
                        "\n模式：" +
                        str(i["mode"]) +
                        "\n地图：" +
                        str(i["currentMap"]) +
                        "\n区服：" +
                        str(i["region"]) +
                        "\n平台：" +
                        str(i["platform"]))
                await query.finish("\n\n".join(results))
        await query.finish("怪起来了，你这指令有问题啊")
    await query.finish("版本只能是bf1/bf4/bfv，别搞错了哦")