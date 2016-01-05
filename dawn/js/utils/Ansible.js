import zmq from 'zmq';
import AppDispatcher from '../dispatcher/AppDispatcher';

// prepare our sockets
let sendSock = zmq.socket('pair');
let recvSock = zmq.socket('pair');

const SEND_PORT = '12356';
const RECV_PORT = '12355';
const LOCATION = '127.0.0.1';

sendSock.connect('tcp://' + LOCATION + ':' + SEND_PORT);
recvSock.connect('tcp://' + LOCATION + ':' + RECV_PORT);

let Ansible = {
  on(event, callback) {
    return recvSock.on(event, function(buffer) {
      let msg = JSON.parse(buffer.toString()); // parse the buffer
      callback(msg);
    })
  },
  send(obj) {
    return sendSock.send(JSON.stringify(obj));
  },
  sendMessage(msgType, content) {
    let msg = {
      header: {
        msg_type: msgType
      },
      content: content
    };
    this.send(msg);
  }
};

// Hack for Ansible messages to enter Flux flow
Ansible.on('message', function(message) {
  // reformat for flux action
  let unpackedMsg = message.content;
  unpackedMsg.type = message.header.msg_type;
  AppDispatcher.dispatch(unpackedMsg);
})

export default Ansible;
