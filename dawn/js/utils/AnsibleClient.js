import AppDispatcher from '../dispatcher/AppDispatcher';
var AnsibleClient = null;

if (process.browser) {
  var socket = require('socket.io-client')(window.location.origin + '/ansible');
  // window.location.origin is an awful hack because
  // open source sucks sometimes.
  // https://github.com/socketio/socket.io-client/issues/812

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
    AppDispatcher.dispatch(message);

  });

  AnsibleClient = socket;
}

export default AnsibleClient;
