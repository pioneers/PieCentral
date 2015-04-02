// Hello World server in Node.js
// Connects REP socket to tcp://*:5560
// Expects "Hello" from client, replies with "World"

var zmq = require('zmq')
  , responder = zmq.socket('rep');
console.log("Running the server...");
responder.connect('tcp://localhost:5555');
responder.on('message', function(msg) {
  console.log('received request:', msg.toString());
  setTimeout(function() {
    responder.send("World");
  }, 1000);
});