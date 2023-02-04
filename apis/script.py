from pathlib import Path

from sanic import Request, Blueprint
from sanic.response import text

bp_script = Blueprint('script', url_prefix='script')


@bp_script.get('/<aid:str>/install.sh', name='install_sh')
async def install_sh(request: Request, aid):
    content_type = 'application/x-shellscript'
    agent_py_url = request.url_for(f'script.nq-agent-py', aid=aid)
    agent_sh_url = request.url_for('script.nq-agent-sh')
    content = Path('script/install.sh').read_text()
    content = content.replace('%agent_py_url%', agent_py_url)
    content = content.replace('%agent_sh_url%', agent_sh_url)

    headers = {'accept-ranges': 'bytes'}
    return text(f'{content}\n', content_type=content_type, headers=headers)


@bp_script.get('/<aid:str>/nq-agent.py', name='nq-agent-py')
async def nq_agent(request: Request, aid):
    agent_api = request.url_for('api.agent', aid=aid)

    content = Path('script/nq-agent.py').read_text()
    content = content.replace('%AGENT_API%', agent_api)
    headers = {'accept-ranges': 'bytes'}
    return text(content, headers=headers)


@bp_script.get('/nq-agent.sh', name='nq-agent-sh')
async def nq_agent(request: Request):
    content_type = 'application/x-shellscript'
    content = Path('script/nq-agent.sh').read_text()
    headers = {'accept-ranges': 'bytes'}
    return text(content, content_type=content_type, headers=headers)


@bp_script.get('/uninstall.sh')
async def uninstall(request: Request):
    content_type = 'application/x-shellscript'
    content = Path('script/uninstall.sh').read_text()
    headers = {'accept-ranges': 'bytes'}
    return text(content, content_type=content_type, headers=headers)
