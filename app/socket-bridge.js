module.exports = function socketBridge(app) {
  var io = require('socket.io')(app);
  var ansible = require('./ansible');

  io.on('connection', function (socket) {
    console.log('Socket.io connected.');
    ansible.on('message', function (data) {
      if (data.header != null &&
        data.header.msg_type != null) {
        socket.emit(data.header.msg_type, data);
        console.log('Passing data to client on event ' + data.header.msg_type + ':');
      } else { // fall back
        console.log('Passing data to client:');
        socket.send(data);
      }
      console.log(data);
    });

    socket.on('message', function (data) {
      ansible.send(data);
      console.log('Passing data to runtime:');
      console.log(data);
    });
  });
  return io;
}
