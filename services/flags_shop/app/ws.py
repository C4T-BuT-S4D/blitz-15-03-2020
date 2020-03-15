from aiohttp import web, WSMsgType
import random, json
from app import ws_logic


class WsHandler:
    def __init__(self, redis, mongo, mysql):
        self._redis = redis
        self._mongo = mongo
        self._mysql = mysql

    @property
    def mongo(self):
        return self._mongo

    async def ws(self, request):
        ws_current = web.WebSocketResponse()
        ws_ready = ws_current.can_prepare(request)
        if not ws_ready.ok:
            return web.json_response({'Error': "WebSocket not ready !"}, content_type='application/json')
        await ws_current.prepare(request)

        id = random.randint(0, 2000000000)
        await ws_current.send_json({'action': 'connect', 'id': id})

        request.app['websockets'][id] = ws_current

        while True:
            msg = await ws_current.receive()
            if msg.type == WSMsgType.text:
                try:
                    json_recv = json.loads(msg.data)
                except:
                    await ws_current.send_json({'Error': 'Json is required'})
                    break

                action = json_recv['action']
                data = json_recv['data']

                if not action or not data:
                    await ws_current.send_json({'Error': 'I need action and data'})

                if action in ws_logic.ACTIONS:
                    result = await ws_logic.validate_action(self._redis, self._mongo, self._mysql, action, data)
                    await ws_current.send_json({'Response': result})
                else:
                    await ws_current.send_json({'Error': 'No such action'})

            else:
                break
        del request.app['websockets'][id]

        return ws_current
