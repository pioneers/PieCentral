async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print 'async_mode is ' + async_mode

if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()

from threading import Thread
from Queue import Empty
import json
import time
from flask import Flask, copy_current_request_context, request
from flask.ext.socketio import SocketIO

# A Flask server with the Socket.IO extension to communicate with Dawn.
def ansible_server(send_queue, recv_queue):
    app = Flask(__name__)
    socketio = SocketIO(app)

    @socketio.on('message')
    def receive_message(msg):
        data = json.loads(msg)
        # Special channel for gamepad data
        if data['header']['msg_type'] == 'gamepad':
            mc.set('gamepad', data['content'])
        else:
            recv_queue.put_nowait(data)

    @socketio.on('connect')
    def on_connect():
        print 'Connected to Dawn.'

    @socketio.on_error()
    def on_error(e):
        print e

    def send_process(send_queue):
        while True:
            try:
                msg = send_queue.get_nowait()
                socketio.emit('message', msg)
                time.sleep(.02)
            except Empty:
                time.sleep(.02)

    send_p = Thread(target=send_process, args=(send_queue,))
    send_p.daemon = True
    send_p.start()

    socketio.run(app)

