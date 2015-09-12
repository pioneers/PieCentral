import debugLib from 'debug';

var debug = debugLib('socket-bridge');

export default function socketBridge(app) {
  var io = require('socket.io')(app);
  var ansibleIo = io.of('/ansible');
  var ansibleToPython = require('./ansible');

  ansibleIo.on('connection', function (socket) {
    console.log('Socket.io connected to socket-bridge');
    debug('Socket.io connected.');
    ansibleToPython.on('message', function (data) {
      if (data.header != null &&
        data.header.msg_type != null) {
        socket.emit(data.header.msg_type, data);
        debug('Passing data to client on event ' + data.header.msg_type + ':');
      } else { // fall back
        debug('Passing data to client:');
        socket.send(data);
      }
      debug(data);
    });

    socket.on('message', function (data) {
      ansibleToPython.send(data);
      debug('Passing data to runtime:');
      debug(data);
    });
  });
  return io;
}
