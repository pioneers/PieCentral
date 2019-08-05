const http = require('http');
const path = require('path');
const express = require('express');
const socketio = require('socket.io');
const bodyParser = require('body-parser');

module.exports = function(logger, { mode }) {
  let app = express();
  app.use(bodyParser());
  let server = http.Server(app);
  let io = socketio(server);

  app.get('/api/schedule', (req, res) => {
    res.send('OK!\n');
  });

  app.put('/api/schedule', (req, res) => {
    logger.info(JSON.stringify(req.body));
    logger.info(JSON.stringify(req.headers));
    res.send('OK!\n');
  });

  app.get('/api/match/:matchId', (req, res) => {
  });

  app.put('/api/match/:matchId', (req, res) => {
  });

  if (mode === 'production') {
    app.get('/', (req, res) => {
      res.sendFile(path.join(__dirname, '../dist/index.html'));
    });

    app.get('/bundle.js', (req, res) => {
      res.sendFile(path.join(__dirname, '../dist/bundle.js'));
    });
  }

  io.on('connection', function(socket) {
    socket.emit('resources', [
      {name: 'Team 42', type: 'ROBOT', status: 'OK'},
      {name: 'Team 43', type: 'ROBOT', status: 'OK'},
    ]);

    // For testing purposes
    setInterval(() => {
      // logger.debug('Timer firing');
      let totalDuration = 30*1000;
      let remainingDuration = totalDuration - new Date().getTime() % totalDuration;
      socket.emit('timer', {
        mode: 'AUTO',
        totalDuration,
        remainingDuration
      });
    }, 100);
  });

  return { server, io };
};
