from collections import deque
import json
import gevent
import app as app_module
from flask_sockets import Sockets
from geventwebsocket.exceptions import WebSocketError


message_queue = deque()

def handle_socket_push(**kwargs):
    message_queue.append(kwargs)

app_module.socket_push = handle_socket_push


sockets = Sockets(app_module.app)


@sockets.route('/display/socket')
def echo(ws):
    while not ws.closed:
        if len(message_queue) > 0:
            blob = json.dumps(message_queue.popleft())
            try:
                ws.send(blob)
            except WebSocketError:
                break
        gevent.sleep()


app = app_module.app
