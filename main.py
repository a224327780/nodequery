import os
from traceback import format_exc

from aiohttp import ClientSession, TCPConnector
from aioredis import from_url
from sanic import Sanic
from sanic import json as json_response
from sanic.log import logger

from apis.api import bp_api
from apis.home import bp_home
from apis.script import bp_script
from utils import config
from utils.common import fail, success
from utils.db import DB
from utils.log import DEFAULT_LOGGING
from utils.task import check_online

app = Sanic('nodequery', log_config=DEFAULT_LOGGING)
app.config.update_config(config)

app.static('/favicon.ico', 'static/favicon.png')

app.blueprint(bp_api)
app.blueprint(bp_script)
app.blueprint(bp_home)

if config.PROD:
    app.add_task(check_online(app))


@app.middleware('response')
def add_cors_headers(request, response):
    headers = {
        "Access-Control-Allow-Methods": "PUT, GET, POST, DELETE, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        'Access-Control-Request-Headers': '*',
        "Access-Control-Allow-Credentials": "true",
        'X-Request-ID': request.id
    }
    response.headers.update(headers)


@app.exception(Exception)
async def catch_anything(request, exception):
    message = exception.message if hasattr(exception, 'message') and exception.message else repr(exception)
    code = 500
    if hasattr(exception, 'status_code'):
        code = exception.status_code
    elif hasattr(exception, 'status'):
        code = exception.status
    logger.exception(exception)
    data = fail(message, format_exc(), code)
    if code == 777:
        code = 200
        data = success()
    return json_response(data, code)


@app.listener('before_server_start')
async def setup_db(_app: Sanic, loop) -> None:
    DB.init_db(loop, 'db0', 'agent')
    _app.ctx.redis = await from_url(config.REDIS_URI, decode_responses=True)
    _app.ctx.request_session = ClientSession(loop=loop, connector=TCPConnector(ssl=False, loop=loop))


@app.listener('before_server_stop')
async def close_db(_app: Sanic, loop) -> None:
    DB.close_db()
    await _app.ctx.redis.close()
    await _app.ctx.request_session.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), access_log=config.DEV, dev=False, fast=config.PROD)
