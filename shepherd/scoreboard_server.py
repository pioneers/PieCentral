import json
import threading
import time
import gevent #pylint: disable=import-error
import gevent.queue # pylint: disable=import-error
from flask import Flask, render_template # pylint: disable=import-error
from flask_socketio import SocketIO, emit, join_room, leave_room, send # pylint: disable=import-error
from Utils import *
from LCM import *

HOST_URL = "192.168.128.129" # "127.0.0.1"
PORT = 5500

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
def hello():
    return "go to /Scoreboard.html"

@app.route('/Scoreboard.html/')
def scoreboard():
    return render_template('Scoreboard.html')

def receiver():

    events = gevent.queue.Queue()
    lcm_start_read(str.encode(LCM_TARGETS.SCOREBOARD), events)

    while True:
        if not events.empty():
            event = events.get_nowait()
            print("RECEIVED:", event)
            if event[0] == SCOREBOARD_HEADER.SCORE:
                socketio.emit(SCOREBOARD_HEADER.SCORE, json.dumps(event[1], ensure_ascii=False))

            elif event[0] == SCOREBOARD_HEADER.TEAMS:
                socketio.emit(SCOREBOARD_HEADER.TEAMS, json.dumps(event[1], ensure_ascii=False))

            elif event[0] == SCOREBOARD_HEADER.RESET_TIMERS:
                socketio.emit(SCOREBOARD_HEADER.RESET_TIMERS,
                              json.dumps(event[1], ensure_ascii=False))

            elif event[0] == SCOREBOARD_HEADER.STAGE_TIMER_START:
                socketio.emit(SCOREBOARD_HEADER.STAGE_TIMER_START,
                              json.dumps(event[1], ensure_ascii=False))

            elif event[0] == SCOREBOARD_HEADER.STAGE:
                socketio.emit(SCOREBOARD_HEADER.STAGE,
                              json.dumps(event[1], ensure_ascii=False))

            elif event[0] == SCOREBOARD_HEADER.LAUNCH_BUTTON_TIMER_START:
                socketio.emit(SCOREBOARD_HEADER.LAUNCH_BUTTON_TIMER_START,
                              json.dumps(event[1], ensure_ascii=False))

            elif event[0] == SCOREBOARD_HEADER.PERKS_SELECTED:
                socketio.emit(SCOREBOARD_HEADER.PERKS_SELECTED,
                              json.dumps(event[1], ensure_ascii=False))

            elif event[0] == SCOREBOARD_HEADER.APPLIED_EFFECT:
                socketio.emit(SCOREBOARD_HEADER.APPLIED_EFFECT,
                              json.dumps(event[1], ensure_ascii=False))

            elif event[0] == SCOREBOARD_HEADER.OVERDRIVE_START:
                socketio.emit(SCOREBOARD_HEADER.OVERDRIVE_START,
                              json.dumps(event[1], ensure_ascii=False))
            #if event[0] == SCOREBOARD_HEADER.ALL_INFO):
            #    socketio.emit('server-to-gui-all-info', json.dumps(event[1], ensure_ascii=False))
        socketio.sleep(0.1)

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)
