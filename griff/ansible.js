var zmq = require('zmq');

// prepare our sockets
var send_sock = zmq.socket('pair');
var recv_sock = zmq.socket('pair');

var SEND_PORT = '12356';
var RECV_PORT = '12355';

send_sock.connect('tcp://localhost:' + SEND_PORT);
recv_sock.connect('tcp://localhost:' + RECV_PORT);

// Exports

// Use something like ansible.on('message', callback)

module.exports.on = function on(event, listener) {
  return recv_sock.on(event, function(buffer) {
    msg = JSON.parse(buffer.toString()); // parse the buffer
    listener(msg);
  });
}

module.exports.send = function send(obj) {
  return send_sock.send(JSON.stringify(obj));
}
