#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot

# Custom your logger
# 
# from nonebot.log import logger, default_format
# logger.add("error.log",
#            rotation="00:00",
#            diagnose=False,
#            level="ERROR",
#            format=default_format)

# You can pass some keyword args config to init function
nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)
app = nonebot.get_asgi()

nonebot.load_from_toml("pyproject.toml")
nonebot.run()
