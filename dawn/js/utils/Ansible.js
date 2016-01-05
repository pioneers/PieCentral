import zmq from 'zmq';
import AppDispatcher from '../dispatcher/AppDispatcher';

// Prepare our sockets for connecting with runtime Ansible.
let sendSock = zmq.socket('pair');
let recvSock = zmq.socket('pair');

const SEND_PORT = '12356';
const RECV_PORT = '12355';
const LOCATION = '127.0.0.1';

sendSock.bind('tcp://' + LOCATION + ':' + SEND_PORT);
recvSock.bind('tcp://' + LOCATION + ':' + RECV_PORT);

/*
 * Module for communicating with the runtime.
 */
let Ansible = {
  /* 
   * Receives data from runtime over ZMQ, and passes it to a callback.
   * Example usage: 'Ansible.on('message', function(msg) {...})'
   */
  on(event, callback) {
    return recvSock.on(event, function(buffer) {
      let msg = JSON.parse(buffer.toString()); // parse the buffer
      callback(msg);
    });
  },
  /* Private, use sendMessage */
  _send(obj) {
    return sendSock.send(JSON.stringify(obj));
  },
  /* Send data over ZMQ to the runtime */
  sendMessage(msgType, content) {
    let msg = {
      header: {
        msg_type: msgType
      },
      content: content
    };
    this._send(msg);
  }
};

/*
 * Hack for Ansible messages to enter Flux flow.
 * Received messages are dispatched as actions,
 * with action's type deteremined by msg_type
 */
Ansible.on('message', function(message) {
  // Reformat as flux action
  let unpackedMsg = message.content;
  unpackedMsg.type = message.header.msg_type;
  AppDispatcher.dispatch(unpackedMsg);
})

export default Ansible;
