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

  AnsibleClient = socket;
}

export default AnsibleClient;
