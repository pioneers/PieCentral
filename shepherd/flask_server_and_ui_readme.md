
# Running the server
In the command line:

    pip install flask-socketio
    pip install gevent
    export FLASK_APP=[SERVER_NAME.py]
    flask run

Go to localhost:[PORTNUM]/[page_name.html] in a browser.

### 2018 Configurations:
#### UI:
Server Name: server.py

Port: 5000

Pages: RFID_control.html, score_adjustment.html, staff_gui.html

#### Scoreboard:
Server Name: scoreboard_server.py

Port: 5500

Pages: Scoreboard.html

#### Dawn:
Server Name: dawn_server.py

Port: 7000



# Server-side modifications

Reading the official flask-socketio and socket.io docs may help get you started with the socket stuff used here: https://flask-socketio.readthedocs.io/en/latest/ and https://socket.io/docs/.

Jinja is a general purpose templating language, but here it is basically used as an HTML template that is compatible with Python. For more about Jinja, go check the official docs: http://jinja.pocoo.org/docs/2.10/.

## Fill in a unique port number not used by another server or by local machine processes
Change the line:
```python
PORT = (NUM)
```

## Serving a new page with a Jinja template
Registers a certain app route with a specific Jinja template:
```python
@app.route('/page.html/')
def page():
    return render_template('page.html')
```
The page.html should be in the 'templates' folder.

Additionally, the main thing for compatibility with the PiE servers is that anywhere a static dependency would have been linked to in HTML, it must be replaced with a Jinja url_for() call:
```javascript
<script type="text/javascript" src="socket.io.js"></script>
```
becomes
```javascript
<script type="text/javascript" src={{url_for( 'static', filename='socket.io.js' )}}></script>
```

The socket.io.js file should be in the 'static' folder.


## Receiving message from UI and forwarding it to LCM
Use the @socketio.on decorator to register an event handler to a specific callback:
```python
@socketio.on('ui-to-server-message-event-name')
def ui_to_server_message_name(received_data):
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.TARGET_NAME, json.loads(received_data))
```

## Sending a particular event to UI
Inside the receiver loop, use socketio.emit to send an event name and some data:
```python
if event[0] == UI_HEADER.EVENT_NAME:
    socketio.emit('server-to-ui-message-event-name', json.dumps(event[1], ensure_ascii=False))
```

# Client-side JS modifications

## Receiving a message from the server
Register an event handler to a specific callback using socket.on:
```javascript
socket.on('server-to-ui-message-event-name', function(data) {
    //do stuff
})
```
