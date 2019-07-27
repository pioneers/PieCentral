const fs = require('fs');
const http = require('http');
const path = require('path');
const express = require('express');
const socketio = require('socket.io');

const app = express();
const server = http.Server(app);
const io = socketio(server);

app.get('/', (req, res) => {
  res.send('OK!');
});

// app.get('/api/game', )

module.exports = server;
