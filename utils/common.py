import hashlib
from functools import wraps
from inspect import isawaitable
from datetime import timezone, timedelta, datetime

from sanic import HTTPResponse, Request, response
from sanic.response import ResponseStream


def get_bj_date(add_seconds=None, fmt='%Y-%m-%d %H:%M:%S'):
    sh_tz = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_now = utc_dt.astimezone(sh_tz)
    if add_seconds:
        bj_now += timedelta(seconds=add_seconds)
    return bj_now.strftime(fmt)


def get_utc_date():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc_dt.strftime('%Y-%m-%d %H:%M:%S')


def md5(string: str):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    _md5 = m.hexdigest()
    return _md5[8:-8].upper()


def success(data=None, message=''):
    if not data:
        data = []
    return {'code': 0, 'msg': message, 'data': data}


def fail(message='', data=None, code=1):
    if not data:
        data = []
    return {'code': code, 'msg': message, 'data': data}


def serializer():
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            retval = f(*args, **kwargs)
            if isawaitable(retval):
                retval = await retval
            if type(retval) in [HTTPResponse, ResponseStream]:
                return retval
            if type(retval) != dict or not retval.get('code'):
                retval = success(retval)
            if isinstance(args[0], Request):
                _request: Request = args[0]
                # retval['request-id'] = _request.headers
            return response.json(retval)

        return decorated_function

    return decorator
