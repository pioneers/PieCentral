import AppDispatcher from '../dispatcher/AppDispatcher';
import fs from 'fs';
import { remote } from 'electron';
const storage = remote.require('electron-json-storage');

let defaultAddress = '127.0.0.1';
let socket = null;

function connectToAnsible(runtimeAddress) {
  if (socket !== null) {
    socket.disconnect();
  }
  socket = io('http://' + runtimeAddress + ':5000/');
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
}

function initAnsible() {
  storage.has('runtimeAddress').then((hasKey)=>{
    if (hasKey) {
      storage.get('runtimeAddress').then((data)=>{
        connectToAnsible(data.address);
      });
    } else {
      connectToAnsible(defaultAddress);
      storage.set('runtimeAddress', {
        address: defaultAddress
      }, (err)=>{
        if(err) throw err;
      });
    }
  });
}



/*
 * Module for communicating with the runtime.
 */
let Ansible = {
  reload() {
    initAnsible();
  },
  /* Private, use sendMessage */
  _send(obj) {
    if (socket !== null) {
      return socket.emit('message', JSON.stringify(obj));
    } else {
      console.log('Socket is not initialized!');
    }
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
  },
  prepareUpgrade(filename) {
    fs.readFile(filename, function(err, buf){
      if (err) throw err;
      var filenamelast = filename.split("/").pop();
      buf = buf.toString('base64');
      Ansible.sendMessage(filenamelast, buf);
    });
  }
};

initAnsible();
export default Ansible;
