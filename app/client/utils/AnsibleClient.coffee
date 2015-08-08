socket = require('socket.io-client')()

socket.sendMessage = (msgType, content) ->
  msg = {}
  msg.header = msg_type: msgType
  msg.content = content
  socket.emit('message', msg)

module.exports = socket
