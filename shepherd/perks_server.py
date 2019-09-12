import json
import threading
import time
import queue
import gevent # pylint: disable=import-error
from flask import Flask, render_template # pylint: disable=import-error
from flask_socketio import SocketIO, emit, join_room, leave_room, send # pylint: disable=import-error
from Utils import *
from LCM import *

HOST_URL = "192.168.128.129"
PORT = 5001

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
def hello():
    return "go to /reset.html"

@app.route('/perksUI.html/')
def perksUI():
    return render_template('perksUI.html')

@app.route('/submit.html/')
def submit():
    return render_template('submit.html')

@app.route('/reset.html/')
def reset():
    return render_template('reset.html')

@socketio.on('ui-to-server-selected-perks')
def ui_to_server_perks(perks):
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.APPLY_PERKS, json.loads(perks))
    print("sending perks:", perks)

@socketio.on('ui-to-server-master-robot')
#pylint: disable=function-redefined
def ui_to_server_perks(data):
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.MASTER_ROBOT, json.loads(data))

@socketio.on('ui-to-server-code')
def ui_to_server_code(data):
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.CODE_APPLICATION, json.loads(data))

def receiver():

    events = gevent.queue.Queue()
    lcm_start_read(str.encode(LCM_TARGETS.TABLET), events)

    while True:
        if not events.empty():
            event = events.get_nowait()
            print("RECEIVED:", event)
            if event[0] == TABLET_HEADER.TEAMS:
                socketio.emit(TABLET_HEADER.TEAMS, json.dumps(event[1], ensure_ascii=False))
            if event[0] == TABLET_HEADER.RESET:
                socketio.emit(TABLET_HEADER.RESET, json.dumps(event[1], ensure_ascii=False))
            if event[0] == TABLET_HEADER.COLLECT_CODES:
                socketio.emit(TABLET_HEADER.COLLECT_CODES, json.dumps(event[1], ensure_ascii=False))
            if event[0] == TABLET_HEADER.COLLECT_PERKS:
                socketio.emit(TABLET_HEADER.COLLECT_PERKS, json.dumps(event[1], ensure_ascii=False))
            if event[0] == TABLET_HEADER.CODE:
                socketio.emit(TABLET_HEADER.CODE, json.dumps(event[1], ensure_ascii=False))

        socketio.sleep(0.1)

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)
