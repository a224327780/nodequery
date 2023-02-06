import json
import math
from urllib import parse

from sanic import Blueprint, Request

from utils.common import serializer, md5, get_bj_date, progress, is_online, format_size, format_date
from utils.db import DB

bp_api = Blueprint('api', url_prefix='api')


@bp_api.get('/agent.list', name='agent_list')
@serializer()
async def agent_list(request: Request):
    data = []
    col = DB.get_col()
    async for item in col.find():
        item = format_item(item)
        data.append(item)
    return data


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


@bp_api.websocket('/agent/<aid:str>', name='agent_data')
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
            data['update_date'] = get_bj_date()
            await col.update_one({'_id': aid}, {'$set': data})
        if 'uid' in 'data':
            data = await col.find_one({'_id': aid})
            data = format_item(data)

        if type(data) != str:
            data = json.dumps(data)
        await ws.send(data)


def format_item(item):
    item['ram'] = math.ceil(progress(item['ram_usage'], item['ram_total']))
    item['disk'] = math.ceil(progress(item['disk_usage'], item['disk_total']))
    item['load'] = math.ceil(progress(item['load'].split(' ')[0], item['cpu_cores']))
    item['is_online'] = is_online(item['update_date'])
    item['date'] = format_date(item['update_date'])
    item['rx_gap'] = format_size(int(item['rx_gap']))
    item['tx_gap'] = format_size(int(item['tx_gap']))
    return item
