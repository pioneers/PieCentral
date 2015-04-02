var zmq = require('zmq');
var PORT = '12355';

// socket to talk to server
var sock = zmq.socket('pair');

sock.connect('tcp://localhost:' + PORT);

sock.send_json = function send_json(obj) {
  return this.send(JSON.stringify(obj))
}

sock.on('message', function (buffer) {
  msg = JSON.parse(buffer.toString()); // parse the buffer
  console.log('Got message:');
  console.log(msg);
  msg.resp = 'awesome response';
  console.log('Sending back:');
  console.log(msg);
  sock.send_json(msg);
});

