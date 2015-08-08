import AppDispatcher from '../dispatcher/AppDispatcher';
var AnsibleClient = null;

if (process.browser) {
  var socket = require('socket.io-client')();

  socket.sendMessage = (msgType, content) => {
    var msg = {
      header: {
        msg_type: msgType
      },
      content: content
    };
    socket.emit('message', msg);
  };

  // Kluge for processing ansible messages as
  // Flux events.
  socket.on('message', (message) => {
    // Also emits the specific ansible msg_type, with no filtering.
    // We'll have to figure out later if this is what we want to do.
    AppDispatcher.dispatch({
      type: message.header.msg_type,
      ansible: true,
      content: message.content
    });

  });

  AnsibleClient = socket;
}

export default AnsibleClient;
