import { ipcMain } from 'electron';
import os from 'os';
import _ from 'lodash';
import RuntimeClient from 'runtime-client';
import RendererBridge from './RendererBridge';

import { append } from '../renderer/actions/console';
import { addHeartbeat } from '../renderer/actions/connection';
import { updateSensors } from '../renderer/actions/devices';

const getIPAddress = (family = 'IPv4', internal = false) => {
  let interfaces = os.networkInterfaces();
  let addresses = _.flatten(_.values(interfaces));
  addresses = _.filter(addresses, address => address.family === family && !address.internal);
  return _.head(_.map(addresses, ({ address }) => address));
};

class Client {
  constructor() {
    this.bindIPCHandlers = this.bindIPCHandlers.bind(this);
    this.unbindIPCHandlers = this.unbindIPCHandlers.bind(this);
    this.disconnect = this.disconnect.bind(this);
  }

  async connect(event, host) {
    this.disconnect();
    this.host = host;
    this.client = new RuntimeClient(host);
    await this.client.connectAll();
    event.returnValue = true;

    await Promise.all([
      this.listenForLogRecords(this.client),
      this.listenForDatagrams(this.client),
    ]);
  }

  async listenForLogRecords(client) {
    try {
      while (true) {
        let record = await client.recvLog();
        if (record) {
          RendererBridge.reduxDispatch(append(record));
        }
      }
    } catch {
      console.log('Stopping log listener.');
    }
  }

  async listenForDatagrams(client) {
    try {
      while (true) {
        let datagram = await client.recvDatagram();
        if (datagram) {
          RendererBridge.reduxDispatch(addHeartbeat());
          RendererBridge.reduxDispatch(updateSensors(datagram));
        }
      }
    } catch {
      console.log('Stopping sensor update listener.');
    }
  }

  async sendDatagram(event, gamepads, host) {
    let defaultHost = getIPAddress();
    if (this.client) {
      await this.client.sendDatagram(gamepads, host || defaultHost);
    }
  }

  async sendCommand(event, commandName, args) {
    if (this.client) {
      event.returnValue = await this.client.sendCommand(commandName, args);
    } else {
      event.returnValue = null;
    }
  }

  disconnect() {
    if (this.client) {
      this.client.closeAll();
      this.host = null;
      this.client = null;
    }
  }

  bindIPCHandlers() {
    ipcMain.on('connect', this.connect.bind(this));
    ipcMain.on('sendDatagram', this.sendDatagram.bind(this));
    ipcMain.on('sendCommand', this.sendCommand.bind(this));
    ipcMain.on('disconnect', this.disconnect.bind(this));
  }

  unbindIPCHandlers() {
    ipcMain.removeAllListeners('connect');
    ipcMain.removeAllListeners('sendDatagram');
    ipcMain.removeAllListeners('sendCommand');
    ipcMain.removeAllListeners('disconnect');
  }
}

const CLIENT = new Client();
export default CLIENT;
