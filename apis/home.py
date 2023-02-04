import os

from sanic import Request, Blueprint
from sanic.response import empty

from utils.common import serializer, get_bj_date, get_utc_date

bp_home = Blueprint('home')


@bp_home.get('/', name='index')
@serializer()
async def index(request: Request):
    return []


@bp_home.get('/ip2', name='ip')
@serializer()
async def get_ip(request: Request):
    headers = {a: b for a, b in request.headers.items()}
    data = {
        'ip': request.remote_addr,
        'ip2': request.ip,
        'request': request.url,
        'forwarded': request.forwarded,
        'headers': headers,
        'host': request.host,
        'bj_date': get_bj_date(),
        'utc_date': get_utc_date()
    }
    return data


@bp_home.get('/robot.txt', name='robot_file')
async def robot_file(request):
    return empty()


@bp_home.get('/e1')
@serializer()
async def envs(request):
    return dict(os.environ)
