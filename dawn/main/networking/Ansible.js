import _ from 'lodash';
import RuntimeClient from 'runtime-client';
import { ipcMain } from 'electron';
import { Logger } from '../../renderer/utils/utils';

const Ansible = {
  logger: new Logger('ansible', 'Ansible Debug'),
  conn: null,
  setup() {
    let host = null;

    ipcMain.handle('ipAddress', async (event, { ipAddress }) => {
      this.close();
      this.conn = new RuntimeClient(ipAddress);
    });

    ipcMain.handle('stateUpdate', async (event, data) => {
      if (this.conn !== null) {
        let gamepads = _.mapValues(data.gamepads, ({ axes, buttons }) => {
          let gamepad = {
            lx: axes[0],
            ly: axes[1],
            rx: axes[2],
            ry: axes[3],
            ...(_.zipObject(RuntimeClient.BUTTONS, buttons)),
          };
          return gamepad;
        });
        await this.conn.sendDatagram(gamepads, host);
      }
    });

    ipcMain.on('studentCodeStatus', (event, { studentCodeStatus }) => {
      console.log(studentCodeStatus);
    });
  },
  close() {
    if (this.conn !== null) {
      this.conn.closeAll();
    }
  },
};

export default Ansible;
