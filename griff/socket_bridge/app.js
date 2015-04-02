var app = require('http').createServer(function () {});
var io = require('socket.io')();

PORT = 12345

app.listen(PORT);

io.on('connection', function (socket) {
    console.log('connected');
});
