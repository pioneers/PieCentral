import json
import threading
import time
import queue
import gevent
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from Utils import *
from LCM import *

HOST_URL = "127.0.0.1"
PORT = 6000

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
socketio = SocketIO(app)

def receiver():

    events = gevent.queue.Queue()
    lcm_start_read(str.encode(LCM_TARGETS.UI), events)

    while True:
        if not events.empty():
            event = events.get_nowait()
            print("RECEIVED:", event)
            if event[0] == SCOREBOARD_HEADER.SCORE:
                socketio.emit(SCOREBOARD_HEADER.SCORE, json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.TEAMS:
                socketio.emit(SCOREBOARD_HEADER.TEAMS, json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.BID_TIMER_START:
                socketio.emit(SCOREBOARD_HEADER.BID_TIMER_START,
                              json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.BID_AMOUNT:
                socketio.emit(SCOREBOARD_HEADER.BID_AMOUNT,
                              json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.GOAL_OWNED:
                socketio.emit(SCOREBOARD_HEADER.GOAL_OWNED,
                              json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.STAGE:
                socketio.emit(SCOREBOARD_HEADER.STAGE, json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.STAGE_TIMER_START:
                socketio.emit(SCOREBOARD_HEADER.STAGE_TIMER_START,
                              json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.POWERUPS:
                socketio.emit(SCOREBOARD_HEADER.POWERUPS, json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.ALLIANCE_MULTIPLIER:
                socketio.emit(SCOREBOARD_HEADER.ALLIANCE_MULTIPLIER,
                              json.dumps(event[1], ensure_ascii=False))
            #if event[0] == SCOREBOARD_HEADER.ALL_INFO):
            #    socketio.emit('server-to-gui-all-info', json.dumps(event[1], ensure_ascii=False))
        socketio.sleep(1)

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)
