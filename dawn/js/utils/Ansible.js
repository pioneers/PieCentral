import AppDispatcher from '../dispatcher/AppDispatcher';
import { remote } from 'electron';
const storage = remote.require('electron-json-storage');

let defaultAddress = '127.0.0.1';

storage.has('runtimeAddress').then((hasKey)=>{
  if (hasKey) {
    storage.get('runtimeAddress').then((data)=>{
      initAnsible(data.address);
    });
  } else {
    initAnsible(defaultAddress);
    storage.set('runtimeAddress', {
      address: defaultAddress
    }, (err)=>{
      if(err) throw err;
    });
  }
});

function initAnsible(runtimeAddress) {
  let socket = io('http://' + runtimeAddress + ':5000/');
  socket.on('connect', ()=>console.log('Connected to runtime.'));
  socket.on('connect_error', (err)=>console.log(err));

  /*
   * Hack for Ansible messages to enter Flux flow.
   * Received messages are dispatched as actions,
   * with action's type deteremined by msg_type
   */
  socket.on('message', (message)=>{
    let transportName = socket.io.engine.transport.name;
    if (transportName !== 'websocket') {
      console.log('Websockets not working! Using:', transportName);
    }
    let unpackedMsg = message.content;
    unpackedMsg.type = message.header.msg_type;
    AppDispatcher.dispatch(unpackedMsg);
  });

  /* Private, use sendMessage */
  Ansible._send = function(obj) {
    return socket.emit('message', JSON.stringify(obj));
  };

  /* Send data over ZMQ to the runtime */
  Ansible.sendMessage = function(msgType, content) {
    let msg = {
      header: {
        msg_type: msgType
      },
      content: content
    };
    Ansible._send(msg);
  }
}

/*
 * Module for communicating with the runtime.
 */
let Ansible = {};

export default Ansible;
