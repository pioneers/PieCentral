var zmq = require('zmq');
var SEND_PORT = '12356';
var RECV_PORT = '12355'

// socket to talk to server
var send_sock = zmq.socket('pair');
var recv_sock = zmq.socket('pair');

send_sock.connect('tcp://localhost:' + SEND_PORT);
recv_sock.connect('tcp://localhost:' + RECV_PORT);

send_sock.send_json = function send_json(obj) {
  return this.send(JSON.stringify(obj))
}

recv_sock.on('message', function (buffer) {
  msg = JSON.parse(buffer.toString()); // parse the buffer
  console.log('Got message:');
  console.log(msg);
  msg.resp = 'awesome response';
  console.log('Sending back:');
  console.log(msg);
  send_sock.send_json(msg);
});

