from collections import deque
import gevent
import app as app_module
from flask_sockets import Sockets


message_queue = deque()

def handle_socket_push(**kwargs):
    message_queue.append(kwargs)

app_module.socket_push = handle_socket_push


sockets = Sockets(app_module.app)


@sockets.route('/display/socket')
def echo(ws):
    # print('\n'.join(dir(ws)))
    while not ws.closed:
        if len(message_queue) > 0:
            ws.send(message_queue.popleft())
        gevent.sleep()


app = app_module.app
