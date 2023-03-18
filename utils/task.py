import asyncio

from aiohttp import ClientSession
from aioredis import Redis
from sanic.log import logger

from utils.common import is_online
from utils.db import DB


async def check_online(app):
    col = DB.get_col('agent')
    request_session = ClientSession()
    api = 'https://api01.eu.org/tg/message'
    status_map = {}
    request_session = app.ctx.request_session
    redis: Redis = app.ctx.redis

    while True:
        if await redis.set('check_online_lock', 1, ex=300, nx=True):
            async for item in col.find():
                try:
                    name = item['name']
                    message = None
                    if not is_online(item['update_date']):
                        message = f'[{name}] [🔴 Down]'
                        status_map[name] = True
                    elif name in status_map:
                        message = f'[{name}] [✅ Up] '
                        del status_map[name]
                    if message:
                        async with request_session.post(api, data={'message': message}, timeout=15) as response:
                            logger.info(await response.text())

                except Exception as e:
                    logger.error(f'{e}\n{str(item)}')
        await asyncio.sleep(120)
