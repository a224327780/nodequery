import asyncio
import json
from urllib import parse

from sanic import Blueprint, Request

from utils.common import serializer, md5, get_bj_date, format_item
from utils.db import DB

bp_api = Blueprint('api', url_prefix='api')


@bp_api.websocket('/agent.list', name='agent_list')
async def agent_list(request: Request, ws):
    col = DB.get_col()
    while True:
        data = []
        async for item in col.find():
            item = format_item(item)
            data.append(item)
        data = json.dumps(data)
        await ws.send(data)
        await asyncio.sleep(2)


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


@bp_api.post('/agent/<aid:str>', name='agent_data')
async def agent(request: Request, aid):
    message = request.body
    col = DB.get_col()
    data = dict(parse.parse_qsl(message))
    data['update_date'] = get_bj_date()
    await col.update_one({'_id': aid}, {'$set': data})
    return message
