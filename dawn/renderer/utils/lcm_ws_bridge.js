/*
  LCM WebSocket Bridge: javascript client library

  This library imitates the LCM APIs, and fulfills requests by forwarding them
  to a websocket server.

  PUBLIC API:

    new LCM(websocket_url)
    on_ready(callback)
    subscribe(channel, msg_type, callback)
    unsubscribe(subscription_id)
    publish(channel, msg)

  EXAMPLE CODE:

    let l = new LCM("ws://localhost:8000");

    l.on_ready(function() {
      let sub = l.subscribe("sprocket/health", "health", function(msg) {
        alert(msg.header.seq);
      });

      window.setTimeout(function() {
        l.unsubscribe(sub);
      }, 1000);

      l.publish("/forest/cmd", {
        __type__: "forest_cmd",
        header: {
          __type__: "header",
          seq: 5,
          time: 0
        },
        lights: [[true, true, false],
                 [true, true, false],
                 [true, true, false],
                 [true, true, false],
                 [true, true, false],
                 [true, true, false],
                 [true, true, false],
                 [true, true, false]],
        servos: [0, 0, 0, 0, 0, 0, 0, 0]
      });
    });
*/
import WebSocket from 'ws';


const CircularJSON = require('circular-json');

class LCM {
  constructor(wsUri) {
    this.ws = new WebSocket(wsUri);
    this.ws.onmessage = (evt) => {
      this.delegate(CircularJSON.parse(evt.data));
    };
    this.callbacks = {}; // indexed by subscription id
    this.on_ready = this.on_ready.bind(this);
    this.on_close = this.on_close.bind(this);
    this.ws_send = this.ws_send.bind(this);
    this.delegate = this.delegate.bind(this);
    this.generate_uuid = this.generate_uuid.bind(this);
    this.subscribe = this.subscribe.bind(this);
    this.unsubscribe = this.unsubscribe.bind(this);
    this.publish = this.publish.bind(this);
  }

  on_ready(cb) { // eslint-disable-line camelcase
    // Call the callback once this LCM instance is ready to receive commands
    this.ws.onopen = () => { cb(this); };
  }

  on_close(cb) { // eslint-disable-line camelcase
    // Call the callback once this LCM instance is ready to receive commands
    this.ws.onclose = () => { cb(this); };
  }

  ws_send(type, data) { // eslint-disable-line camelcase
    // Internal convenience method for sending data over the websocket
    try {
      this.ws.send(CircularJSON.stringify({ type, data }));
    } catch (err) {
      console.log('*');
    }
  }

  delegate(request) {
    // Internal method that delegates data received to the appropriate handler
    let callback;
    switch (request.type) {
      case 'packet':
        callback = this.callbacks[request.data.subscription_id];
        if (callback !== undefined) {
          callback(request.data.msg);
        }
        break;
      default:
        throw 'Invalid request!'; // eslint-disable-line no-throw-literal
    }
  }

  generate_uuid() { // eslint-disable-line
    // Internal method to generate unique subscription IDs
    let d = new Date().getTime();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      // eslint-disable-next-line
      const r = (d + Math.random() * 16) % 16 | 0;
      d = Math.floor(d / 16);
      return (c === 'x' ? r : (r & 0x7 | 0x8)).toString(16); // eslint-disable-line
    });
  }

  subscribe(channel, msg_type, callback) { // eslint-disable-line camelcase
    // Subscribe to an LCM channel with a callback
    // Unlike the core LCM APIs, this requires a message type, and the
    // callback receives an already-decoded message as JSON instead of
    // an encoded string
    //
    // Invalid requests are silently ignored (there is no error callback)
    const subscription_id = this.generate_uuid(); // eslint-disable-line camelcase
    this.callbacks[subscription_id] = callback;

    this.ws_send('subscribe', { channel, msg_type, subscription_id });
    return subscription_id; // eslint-disable-line camelcase
  }

  unsubscribe(subscription_id) { // eslint-disable-line camelcase
    // Unsubscribe from an LCM channel, using a subscription id
    //
    // Invalid requests are silently ignored (there is no error callback)

    this.ws_send('unsubscribe', { subscription_id });
    delete this.callbacks[subscription_id];
  }

  publish(channel, data) {
    // Publish a message to an LCM channel
    // Unlike the core LCM APIs, the data is an arbitrary object, not an
    // instance of something special. However, it and any nested types must
    // define a __type__ relative to the TYPES_ROOT of the websocket server
    //
    // Invalid requests are silently ignored (there is no error callback)
    this.ws_send('publish', { channel, data });
  }
}

export default LCM;
