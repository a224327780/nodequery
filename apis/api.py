import asyncio
import json
import math
from urllib import parse

from sanic import Blueprint, Request

from utils.common import serializer, md5, get_bj_date, progress, is_online, format_size, format_date
from utils.db import DB

bp_api = Blueprint('api', url_prefix='api')


@bp_api.websocket('/agent.list', name='agent_list')
async def agent_list(request: Request, ws):
    col = DB.get_col()
    try:
        while True:
            data = []
            async for item in col.find():
                item = format_item(item)
                data.append(item)
            data = json.dumps(data)
            await ws.send(data)
            await asyncio.sleep(2)
    finally:
        await ws.close()


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
    try:
        while True:
            message = await ws.recv(10.0)
            if not message:
                break

            if 'close' in message:
                await ws.close()
                break

            if 'uptime=' in message:
                col = DB.get_col()
                data = dict(parse.parse_qsl(message))
                data['update_date'] = get_bj_date()
                await col.update_one({'_id': aid}, {'$set': data})

            await ws.send(message)
    finally:
        await ws.close()


def format_item(item):
    item['ram'] = math.ceil(progress(item['ram_usage'], item['ram_total']))
    item['disk'] = math.ceil(progress(item['disk_usage'], item['disk_total']))
    item['load'] = int(item['load_cpu'])
    # item['load'] = math.ceil(progress(item['load'].split(' ')[0], item['cpu_cores']))
    item['is_online'] = is_online(item['update_date'])
    item['date'] = item['update_date']
    item['online_day'] = int(int(item['uptime']) / (3600 * 24))
    item['rx_gap'] = format_size(int(item['rx_gap']))
    item['tx_gap'] = format_size(int(item['tx_gap']))
    return item
