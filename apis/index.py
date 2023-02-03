import json
from asyncio.log import logger

from sanic import Blueprint, Request, html

from utils.common import serializer, md5, get_bj_date
from utils.db import DB

bp_api = Blueprint('api', url_prefix='api')


@bp_api.post('/agent.json')
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
        await col.insert_on(data)
    return data


@bp_api.websocket('/agent')
async def agent(request: Request, ws):
    while True:
        data = await ws.recv()
        logger.info(data)
        print(data)
        if 'close' in data:
            break
        await ws.send(data)
