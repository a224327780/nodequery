#!/usr/bin/env python3

import asyncio
import subprocess
import websockets


async def client():
    ws_host = '%AGENT_API%'
    while 1:
        try:
            async with websockets.connect(ws_host) as websocket:
                for _ in range(300):
                    cmd = '/etc/nodequery/nq-agent.sh'
                    output = subprocess.getoutput(cmd)
                    await websocket.send(output)
                    await asyncio.sleep(1)
                    # data = await websocket.recv()
                    # print(data)
            await asyncio.sleep(1)
        except Exception as e:
            print(e)
            await asyncio.sleep(1)
        await asyncio.sleep(3)


asyncio.run(client())
