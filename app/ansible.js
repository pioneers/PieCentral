var zmq = require('zmq');

// prepare our sockets
var sendSock = zmq.socket('pair');
var recvSock = zmq.socket('pair');

var SEND_PORT = '12356';
var RECV_PORT = '12355';

sendSock.connect('tcp://localhost:' + SEND_PORT);
recvSock.connect('tcp://localhost:' + RECV_PORT);

// Exports

// Use something like ansible.on('message', callback)

module.exports.on = function on(event, listener) {
  return recvSock.on(event, function(buffer) {
    var msg = JSON.parse(buffer.toString()); // parse the buffer
    listener(msg);
  });
};

module.exports.send = function send(obj) {
  return sendSock.send(JSON.stringify(obj));
};
