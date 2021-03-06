from decimal import Decimal
from io import BytesIO

import base64
import httpx
import os
import sqlite3
import time
from PIL import Image, ImageDraw, ImageFont
from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
from nonebot.adapters.cqhttp.message import MessageSegment
from nonebot.log import logger
from nonebot.typing import T_State

query = on_command("player")


def cast_to_decimal(num):
    """
    Change a number to an Decimal object to avoid error.

    :param num: Any number that is not converted to the Decimal object.
    :return: An Decimal object that is equivalent to the num parameter passed.
    """
    return Decimal(str(num))


@query.handle()
async def handle_message(bot: Bot, event: Event, state: T_State):
    conn = sqlite3.connect("./localdb/player.db")
    cursor = conn.cursor()
    if len(cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='player_data'").fetchall()) == 0:
        cursor.execute('''
            CREATE TABLE player_data (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                type            TEXT                NOT NULL,
                time            NUMERIC             NOT NULL,
                userName        TEXT                NOT NULL,
                rank            NUMERIC             NOT NULL,
                accuracy        TEXT                NOT NULL,
                headshotRate    TEXT                NOT NULL,
                longestHeadshot NUMERIC             NOT NULL,
                spm             TEXT                NOT NULL,
                kd              TEXT                NOT NULL,
                kpm             TEXT                NOT NULL,
                assists         NUMERIC             NOT NULL,
                kills           NUMERIC             NOT NULL,
                deaths          NUMERIC             NOT NULL,
                wins            NUMERIC             NOT NULL,
                loses           NUMERIC             NOT NULL,
                winPercent      TEXT                NOT NULL
            );
        ''')
        conn.commit()

    sender_id = event.get_user_id()
    args = str(event.get_message()).strip().split(' ')
    if len(args) == 1:
        await query.finish("?????????????????????ID??????????????????")
    if len(args) != 2:
        await query.finish("??????????????????????????????????????????\n?????????#player <bf1/bf4/bfv> <id>???")
    if args[0] in ("bf1", "bf4", "bfv"):
        if args[0] and args[1]:
            logger.debug(
                "Requesting: https://api.gametools.network/" + args[0] + "/stats/?name=" + args[1] + "&lang=" + (
                    "zh-cn" if args[0] == 'bfv' else "zh-tw"))
            async with httpx.AsyncClient() as client:
                try:
                    await query.send("????????????????????????????????????????????????")
                    resp = await client.get(
                        "https://api.gametools.network/" + args[0] + "/stats/?name=" + args[1] + "&lang=" + (
                            "zh-cn" if args[0] == 'bfv' else "zh-tw"), timeout=8.0)
                except httpx.ReadTimeout:
                    await query.finish("???????????????????????????????????????")
                result = resp.json()
                logger.debug(result)
                if "detail" in result:
                    await query.finish("??????????????????ID???????????????")
                text = ("????????????" +
                        str(result["userName"]) +
                        "\n?????????" +
                        str(result["rank"]) +
                        "\n????????????" +
                        str(result["accuracy"]) +
                        "\n????????????" +
                        str(result["headshots"]) +
                        "\n???????????????" +
                        str(result["longestHeadShot"]) +
                        "\nSPM???" +
                        str(result["scorePerMinute"]) +
                        "\nK/D???" +
                        str(result["killDeath"]) +
                        "\nKPM???" +
                        str(result["killsPerMinute"]) +
                        "\n??????????????????" +
                        str(result["killAssists"]) +
                        "\nK???" +
                        str(result["kills"]) +
                        "\nD???" +
                        str(result["deaths"]) +
                        "\nWin???" +
                        str(result["wins"]) +
                        "\nLose???" +
                        str(result["loses"]) +
                        "\n?????????" +
                        str(result["winPercent"])
                        )

                recent = cursor.execute(
                    "SELECT * FROM player_data WHERE userName=? AND type=? ORDER BY id DESC LIMIT 1",
                    (args[1], args[0])
                ).fetchall()

                upgrade_msg = ""
                if len(recent) != 0:
                    upgrade_msg_arr = []
                    if result['rank'] - recent[0][4] > 0:
                        upgrade_msg_arr.append(f"?????????????????????{result['rank'] - recent[0][4]}??????")
                    if cast_to_decimal(result['killDeath']) - cast_to_decimal(recent[0][9]) > 0:
                        upgrade_msg_arr.append(
                            f"??????KD?????????{cast_to_decimal(result['killDeath']) - cast_to_decimal(recent[0][9])}???"
                        )
                    if cast_to_decimal(result['scorePerMinute']) - cast_to_decimal(recent[0][8]) > 0:
                        upgrade_msg_arr.append(
                            f"??????SPM?????????{cast_to_decimal(result['scorePerMinute']) - cast_to_decimal(recent[0][8])}???"
                        )
                    if cast_to_decimal(result['killsPerMinute']) - cast_to_decimal(recent[0][10]) > 0:
                        upgrade_msg_arr.append(
                            f"??????KPM?????????{cast_to_decimal(result['killsPerMinute']) - cast_to_decimal(recent[0][10])}???"
                        )
                    upgrade_msg = "\n".join(upgrade_msg_arr)

                cursor.execute(
                    "INSERT INTO player_data "
                    "(time, type, userName, rank, accuracy, headshotRate, longestHeadshot, spm, "
                    "kd, kpm, assists, kills, deaths, wins, loses, winPercent) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        int(time.time()),
                        args[0],
                        result["userName"],
                        result["rank"],
                        result["accuracy"],
                        result["headshots"],
                        result["longestHeadShot"],
                        result["scorePerMinute"],
                        result["killDeath"],
                        result["killsPerMinute"],
                        result["killAssists"],
                        result["kills"],
                        result["deaths"],
                        result["wins"],
                        result["loses"],
                        result["winPercent"]
                    )
                )

                conn.commit()

                image = Image.open(os.path.join(os.path.abspath('.'), 'static', f'{args[0]}-mod-blur.png'))
                drawer = ImageDraw.Draw(image)
                font = ImageFont.truetype(os.path.join(os.path.abspath('.'), 'static', 'HarmonyOS_Sans_SC_Regular.ttf'),
                                          30)
                drawer.text((50, 50), text, font=font, fill="#000090")
                img_io = BytesIO()
                image.save(img_io, format="PNG")

                await query.finish(
                    Message(
                        (MessageSegment.at(sender_id) if event.get_session_id().startswith('group') else '') +
                        MessageSegment.image("base64://" + base64.b64encode(img_io.getvalue()).decode()) +
                        upgrade_msg
                    )
                )
        await query.finish("???????????????????????????????????????")
    await query.finish("???????????????bf1/bf4/bfv??????????????????")
