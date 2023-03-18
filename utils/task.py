import asyncio

from aiohttp import ClientSession
from sanic.log import logger

from utils.common import is_online
from utils.db import DB


async def check_online():
    col = DB.get_col()
    request_session = ClientSession()
    api = 'https://api01.eu.org/tg/message'
    status_map = {}
    try:
        while True:
            async for item in col.find():
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

            await asyncio.sleep(120)
    except Exception as e:
        logger.error(e)
    finally:
        await request_session.close()
