import asyncio
import json
from urllib import parse

from sanic import Blueprint, Request

from utils.common import serializer, md5, get_bj_date
from utils.db import DB

bp_api = Blueprint('api', url_prefix='api')


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
    # request.app.add_task(ws.keepalive_ping(), name="stream_keepalive")
    while True:
        data = await ws.recv()
        if 'close' in data:
            await ws.close()
            break

        col = DB.get_col()
        if 'uptime=' in data:
            data = dict(parse.parse_qsl(data))
            await col.update_one({'_id': aid}, {'$set': data})
        if 'get' in 'data':
            data = await col.find_one({'_id': aid})

        if type(data) != str:
            data = json.dumps(data)
        await ws.send(data)
