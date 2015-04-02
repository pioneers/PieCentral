PORT = 12345
var io = require('socket.io')(PORT);
var ansible = require('./ansible');

io.on('connection', function (socket) {
  console.log('Socket.io connected.');
  ansible.on('message', function (data) {
    socket.send(data);
    console.log('Passing data to client:');
    console.log(data);
  });

  socket.on('message', function (data) {
    ansible.send(data);
    console.log('Passing data to runtime:');
    console.log(data);
  });
});
