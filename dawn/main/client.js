import { ipcMain } from 'electron';
import RuntimeClient from 'runtime-client';

class Client {
  async connect(host) {
    if (this.client) {
      this.disconnect();
    }
    this.client = new RuntimeClient(host);
    await this.client.connectAll();
  }

  async sendCommand(commandName, args) {
    if (this.client) {
      return await this.client.sendCommand(commandName, args);
    }
  }

  disconnect() {
    this.client.closeAll();
  }
}

const CLIENT = new Client();

export default CLIENT;
