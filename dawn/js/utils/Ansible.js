import AppDispatcher from '../dispatcher/AppDispatcher';
import smalltalk from 'smalltalk';

let runtimeAddress = localStorage.getItem('runtimeAddress') || '127.0.0.1';
let socket = io('http://' + runtimeAddress + ':5000/');
socket.on('connect', ()=>console.log('Connected to runtime.'));
socket.on('connect_error', (err)=>console.log(err));
const BATTERY_LEVEL_TYPE = 'BATTERY_DEAD';

/*
 * Hack for Ansible messages to enter Flux flow.
 * Received messages are dispatched as actions,
 * with action's type deteremined by msg_type
 */
socket.on('message', (message)=>{
  let unpackedMsg = message.content;
  unpackedMsg.type = message.header.msg_type;
  if (unpackedMsg.type == BATTERY_LEVEL_TYPE) {
    smalltalk.alert(
      'Error',
      'Battery level crucial!'
    ).then(()=>{
      return;
    }, ()=>{
      return;
    });
  }
  AppDispatcher.dispatch(unpackedMsg);
});

/*
 * Module for communicating with the runtime.
 */
let Ansible = {
  /* Private, use sendMessage */
  _send(obj) {
    return socket.emit('message', JSON.stringify(obj));
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

export default Ansible;
