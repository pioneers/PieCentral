PORT = 12345
var io = require('socket.io')(PORT);

io.on('connection', function (socket) {
  socket.on('message', function (data) {
    console.log(data);
  });
});
