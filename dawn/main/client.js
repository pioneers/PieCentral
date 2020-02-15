import { ipcMain } from 'electron';
import RuntimeClient from 'runtime-client';
import RendererBridge from './RendererBridge';
import { append, toggle } from '../renderer/actions/console';

class Client {
  constructor() {
    this.bindIPCHandlers = this.bindIPCHandlers.bind(this);
  }

  async connect(event, host) {
    if (this.client) {
      this.disconnect();
    }
    this.client = new RuntimeClient(host);
    await this.client.connectAll();
    event.returnValue = true;

    try {
      while (true) {
        let record = await this.client.recvLog();
        if (record !== undefined) {
          RendererBridge.reduxDispatch(append(record));
        }
      }
    } catch {
      console.log('Exiting!');
    }
  }

  async sendCommand(event, commandName, args) {
    if (this.client) {
      return await this.client.sendCommand(commandName, args);
    }
  }

  disconnect() {
    this.client.closeAll();
  }

  bindIPCHandlers() {
    ipcMain.on('connect', this.connect.bind(this));
    // ipcMain.on('disconnect', this.disconnect.bind(this));
  }
}

const CLIENT = new Client();
export default CLIENT;
