from pathlib import Path

from sanic import Request, Blueprint
from sanic.log import logger
from sanic.response import text

bp_script = Blueprint('script', url_prefix='script')


@bp_script.get('/<aid:str>/install.sh', name='install_sh')
async def install_sh(request: Request, aid):
    content_type = 'application/x-shellscript'
    agent_url = request.url_for(f'script.nq-agent', aid=aid)
    content = Path('script/install.sh').read_text()
    content = content.replace('%agent_url%', agent_url)
    headers = {'accept-ranges': 'bytes'}
    return text(f'{content}\n', content_type=content_type, headers=headers)


@bp_script.get('/<aid:str>/nq-agent.sh', name='nq-agent')
async def nq_agent(request: Request, aid):
    content_type = 'application/x-shellscript'
    agent_api = request.url_for('api.agent.json')

    content = Path('script/nq-agent.sh').read_text()
    content = content.replace('%AGENT_TOKEN%', aid).replace('%AGENT_API%', agent_api)
    headers = {'accept-ranges': 'bytes'}
    return text(f'{content}\n', content_type=content_type, headers=headers)


@bp_script.get('/uninstall.sh')
async def uninstall(request: Request):
    content_type = 'application/x-shellscript'
    content = Path('script/uninstall.sh').read_text()
    headers = {'accept-ranges': 'bytes'}
    return text(content, content_type=content_type, headers=headers)
