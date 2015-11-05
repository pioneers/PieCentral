import debugLib from 'debug';
import socketIo from 'socket.io';

var debug = debugLib('socket-bridge');

export default function socketBridge(app) {
  var io = socketIo(app);
  var ansibleIo = io.of('/ansible');
  var ansibleToPython = require('./ansible');

  ansibleIo.on('connection', function (socket) {
    console.log('Socket.io connected to socket-bridge');
    debug('Socket.io connected.');
    ansibleToPython.on('message', function (data) {
      debug('Message frame ' + Date.now());

      // Send on particular msg_type channel.
      if (data.header != null &&
        data.header.msg_type != null) {
        // socket.emit(data.header.msg_type, data);
        var unpackedMessage = data.content;
        unpackedMessage.type = data.header.msg_type;
        socket.send(unpackedMessage);
        debug('Passing data to client on event ' + data.header.msg_type + ':');
      } else {
        console.log("Didn't get correct type!");
        debug("Didn't get correct type!");
      }
    });

    socket.on('message', function (data) {
      ansibleToPython.send(data);
      debug('Passing data to runtime:');
      debug(data);
    });
  });
  return io;
}
