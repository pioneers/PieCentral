import os from 'os';
import _ from 'lodash';
import RuntimeClient from 'runtime-client';
import { ipcMain } from 'electron';

import RendererBridge from '../RendererBridge';
import { updateConsole } from '../../renderer/actions/ConsoleActions';
import {
  ansibleDisconnect,
  infoPerMessage,
  updateCodeStatus,
} from '../../renderer/actions/InfoActions';
import { updatePeripherals } from '../../renderer/actions/PeripheralActions';
import { robotState, Logger } from '../../renderer/utils/utils';

const getIPAddress = (family = 'IPv4') => {
  const interfaces = os.networkInterfaces();
  let addresses = _.flatten(_.values(interfaces));
  addresses = _.filter(addresses, (address) => address.family === family && !address.internal);
  return _.head(_.map(addresses, ({ address }) => address));
};

const Ansible = {
  logger: new Logger('ansible', 'Ansible Debug'),
  conn: null,
  async recvDatagrams() {
    try {
      for await (const datagram of this.conn.recvDatagrams()) {
        let sensorData = _.map(datagram.devices, ({ type, params }, uid) => {
          return {
            device_type: type,
            uid: uid,
          };
        });
        console.log(sensorData);
        RendererBridge.reduxDispatch(updateCodeStatus(robotState.TELEOP));
        RendererBridge.reduxDispatch(infoPerMessage(2));
        RendererBridge.reduxDispatch(updatePeripherals(sensorData));
      }
    } catch (e) {
      console.log(e);
    }
  },
  async recvLogs() {
    try {
      for await (const log of this.conn.recvLogs()) {
        if (log.logger === 'runtime.game.studentapi' && log.event) {
          RendererBridge.reduxDispatch(updateConsole(`[${log.timestamp}] ${log.event}\n`));
        }
      }
    } catch (e) {
      console.log(e);
    }
  },
  setup() {
    const host = '127.0.0.1' || getIPAddress(); // TODO

    ipcMain.on('ipAddress', (event, { ipAddress }) => {
      this.close();
      this.conn = new RuntimeClient(ipAddress);
      console.log(`Opened client to ${ipAddress}, receiving on ${host}`);
      return this.conn.connectAll()
        .then(() => Promise.all([
          this.recvDatagrams(this.conn),
          this.recvLogs(this.conn),
        ]));
    });

    ipcMain.on('stateUpdate', (event, data) => {
      if (this.conn !== null) {
        const gamepads = _.mapValues(data.gamepads, ({ axes, buttons }) => ({
          joystick_left_x: axes[0],
          joystick_left_y: axes[1],
          joystick_right_x: axes[2],
          joystick_right_y: axes[3],
          ...(_.zipObject(RuntimeClient.BUTTONS, buttons)),
        }));
        return this.conn.sendDatagram(gamepads, host);
      }
    });

    // ipcMain.on('studentCodeStatus', (event, { studentCodeStatus }) => {
    //   console.log(studentCodeStatus);
    // });
  },
  close() {
    if (this.conn !== null) {
      RendererBridge.reduxDispatch(ansibleDisconnect());
      this.conn.closeAll();
    }
  },
};

export default Ansible;
