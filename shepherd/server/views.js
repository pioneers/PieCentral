const fs = require('fs');
const http = require('http');
const path = require('path');
const express = require('express');
const socketio = require('socket.io');

module.exports = function(logger, { mode }) {
  let app = express();
  let server = http.Server(app);
  let io = socketio(server);

  if (mode === 'production') {
    app.get('/', (req, res) => {
      res.sendFile(path.join(__dirname, '../dist/index.html'));
    });

    app.get('/bundle.js', (req, res) => {
      res.sendFile(path.join(__dirname, '../dist/bundle.js'));
    });
  }

  io.on('connection', function(socket) {
    // For testing purposes
    setInterval(() => {
      logger.debug('Timer firing');
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
