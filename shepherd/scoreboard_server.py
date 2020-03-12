import json
import threading
import time
import gevent #pylint: disable=import-error
import gevent.queue # pylint: disable=import-error
from flask import Flask, render_template # pylint: disable=import-error
from flask_socketio import SocketIO, emit, join_room, leave_room, send # pylint: disable=import-error
from Utils import *

HOST_URL = "127.0.0.1" # "127.0.0.1"
PORT = 5500

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
def hello():
    return "go to /ScoreboardScratch.html"

def sender():

    while True:

        new_input = input("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n(a) teams\n(b) reset match\n(c) start auto\n(d) start teleop\n(e) spawn\n(f) finish recipe\n(g) move rat\n(h) move king rat\n(i) health\n(j) penalty\n(k) stop match\n\nInput: ")
        dict = {}

        if new_input == 'a':
            match = input("Match Number: ")
            g1name = input("Gold 1 Name: ")
            g1num = input("Gold 1 Number: ")
            g2name = input("Gold 2 Name: ")
            g2num = input("Gold 2 Number: ")
            b1name = input("Blue 1 Name: ")
            b1num = input("Blue 1 Number: ")
            b2name = input("Blue 2 Name: ")
            b2num = input("Blue 2 Number: ")
            dict = {'match_number': match, 'g1name': g1name, 'g1num': g1num,
                    'g2name': g2name, 'g2num': g2num, 'b1name': b1name,
                    'b1num': b1num, 'b2name': b2name, 'b2num': b2num}
            socketio.emit('teams', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'b':
            socketio.emit('reset_match', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'c':
            socketio.emit('start_match', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'd':
            dict = {'name': input("Recipe name: ")}
            socketio.emit('start_teleop', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'e':
            dict = {'name': input("Recipe name: ")}
            socketio.emit('spawn', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'f':
            dict = {'color': input("Gold = 0, Blue = 1: ")}
            socketio.emit('finish_recipe', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'g':
            dict = {'color': input("Gold = 0, Blue = 1: ")}
            socketio.emit('move_rat_to_gold', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'h':
            dict = {'color': input("Gold = 0, Blue = 1: ")}
            socketio.emit('move_king_rat', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'i':
            socketio.emit('health', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'j':
            dict = {'color': input("Gold = 0, Blue = 1: ")}
            socketio.emit('penalty', json.dumps(dict, ensure_ascii=False))
        elif new_input == 'k':
            socketio.emit('stop_match', json.dumps(dict, ensure_ascii=False))

def receiver():
    print('receive')
    #events = queue.Queue()
    #while True:
    #    event = events.get(True)
    #    print(event)

@app.route('/ScoreboardScratch.html/')
def scoreboard():
    sender_thread = threading.Thread(target=sender, name="DummyScoreboardSender")
    #recv_thread = threading.Thread(target=receiver, name="DummyScoreboardReceiver")
    sender_thread.start()
    #recv_thread.start()
    return render_template('ScoreboardScratch.html')

socketio.run(app, host=HOST_URL, port=PORT)

if __name__ == '__main__':
    print('main')
