import { ipcMain } from 'electron';
import RuntimeClient from 'runtime-client';

class Client {
  async connect(host) {
    if (this.client) {
      this.disconnect();
    }
    this.client = new RuntimeClient(host);
    await this.client.connectAll();
    console.log(await this.client.sendCommand('lint'))
  }

  disconnect() {
    this.client.closeAll();
  }
}

const CLIENT = new Client();

export default CLIENT;
