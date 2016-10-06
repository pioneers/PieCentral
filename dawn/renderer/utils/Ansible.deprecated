import { store } from '../configureStore';
import request from 'superagent';
import { remote, ipcRenderer } from 'electron';
const storage = remote.require('electron-json-storage');

const defaultAddress = '192.168.13.100';
let socket = null;

/*
 * Module for communicating with the runtime.
 */
const Ansible = {
  initAnsible() {
    storage.has('runtimeAddress').then((hasKey) => {
      if (hasKey) {
        storage.get('runtimeAddress').then((data) => {
          Ansible.connectToAnsible(data.address);
        });
      } else {
        Ansible.connectToAnsible(defaultAddress);
        storage.set('runtimeAddress', {
          address: defaultAddress,
        }, (err) => {
          if (err) throw err;
        });
      }
    });
  },

  connectToAnsible(runtimeAddress) {
    // Remove the existing connection.
    if (socket !== null) {
      socket.disconnect();
    }

    socket = io(
      `http://${runtimeAddress}:5000/`,
      { transports: ['websocket'] }
    );

    socket.on('connect', () => {
      store.dispatch({ type: 'ANSIBLE_CONNECT' });
      ipcRenderer.send('runtime-connect');
      console.log('Connected to runtime.');
    });

    socket.on('disconnect', () => {
      store.dispatch({ type: 'ANSIBLE_DISCONNECT' });
      ipcRenderer.send('runtime-disconnect');
      console.log('Disconnected from runtime');
    });

    socket.on('connect_error', (err) => { console.log(err); });

    /*
    * Hack for Ansible messages to enter Flux flow.
    * Received messages are dispatched as actions,
    * with action's type deteremined by msg_type
    */
    socket.on('message', (message) => {
      const transportName = socket.io.engine.transport.name;
      if (transportName !== 'websocket') {
        console.log('Websockets not working! Using:', transportName);
      }
      const unpackedMsg = message.content;
      unpackedMsg.type = message.header.msg_type;
      store.dispatch(unpackedMsg);
    });

    Ansible.runtimeAddress = runtimeAddress;
  },

  reload() {
    Ansible.initAnsible();
  },

  /* Private, use sendMessage */
  send(obj, callback) {
    if (socket !== null) {
      return socket.emit('message', JSON.stringify(obj), (response) => {
        if (callback) {
          callback(response);
        }
      });
    }
    console.log('Console not initialized');
    return null;
  },

  /* Send data over SocketIO to the runtime */
  sendMessage(msgType, content, callback) {
    const msg = {
      header: {
        msg_type: msgType,
      },
      content,
    };
    this.send(msg, callback);
  },

  restartRuntime() {
    if (this.runtimeAddress) {
      request.get(
        `http://${this.runtimeAddress}:5000/restart`).end((err) => {
          if (err) {
            console.log('Error on restart:', err);
          }
        }
      );
    }
  },

  uploadFile(filepath, callback) {
    if (this.runtimeAddress) {
      request
        .post(`http://${this.runtimeAddress}:5000/upload`)
        .attach('file', filepath).end(callback);
    } else {
      console.log('Cannot upload! Not connected to runtime!');
    }
  },
};

Ansible.initAnsible();

export default Ansible;
