import asyncio
import json
from asyncio.log import logger

from sanic import Blueprint, Request

from utils.common import serializer, md5, get_bj_date
from utils.db import DB

bp_api = Blueprint('api', url_prefix='api')


@bp_api.post('/agent.json', name='agent.json')
@serializer()
async def agent(request: Request):
    agent_name = request.form.get('agent_name')
    agent_data = request.form.get('agent_data')
    if type(agent_data) == str:
        agent_data = json.loads(agent_data)

    _id = md5(agent_name)
    col = DB.get_col()
    await col.update_one({'_id': _id}, {'$set': agent_data})
    return {}


@bp_api.post('/agent.add')
@serializer()
async def agent(request: Request):
    agent_name = request.form.get('agent_name')
    _id = md5(agent_name)
    col = DB.get_col()
    data = await col.find_one({'_id': _id})
    if not data:
        data = {'name': agent_name, '_id': _id, 'create_date': get_bj_date()}
        await col.insert_one(data)
    return f"curl {request.url_for(f'script.install_sh', aid=_id)} | bash"


@bp_api.websocket('/agent/<aid:str>', name='agent')
async def agent(request: Request, ws, aid):
    while True:
        data = await ws.recv()
        if not data:
            await asyncio.sleep(1)
            continue

        logger.info(data)
        if 'close' in data:
            break
        await ws.send(data)
