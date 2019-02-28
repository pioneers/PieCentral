import json
import threading
import time
import queue
import gevent # pylint: disable=import-error
from flask import Flask, render_template # pylint: disable=import-error
from flask_socketio import SocketIO, emit, join_room, leave_room, send # pylint: disable=import-error
from Utils import *
from LCM import *

HOST_URL = "0.0.0.0"
PORT = 5500

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
socketio = SocketIO(app)

@app.route('/')
def hello():
    return "go to /perksUI.html"

@app.route('/perksUI.html/')
def scoreboard():
    return render_template('perksUI.html')


@socketio.on('ui-to-server-selected-perks')
def ui_to_server_scores(perks):
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.APPLY_PERKS, json.loads(scores))

def receiver():

    events = gevent.queue.Queue()
    lcm_start_read(str.encode(LCM_TARGETS.SCOREBOARD), events)

    while True:
        if not events.empty():
            event = events.get_nowait()
            print("RECEIVED:", event)
            if event[0] == PERKS_HEADER.TEAMS:
                socketio.emit(PERKS_HEADER.TEAMS, json.dumps(event[1], ensure_ascii=False))

        socketio.sleep(0.1)

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)
