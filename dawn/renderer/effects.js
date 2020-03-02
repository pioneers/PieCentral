import { eventChannel } from 'redux-saga';
import { ipcRenderer } from 'electron';
import { all, delay, fork, put, takeLatest, select } from 'redux-saga/effects';
import { addHeartbeat, setStatus, disconnect } from './actions/connection';
import { ConnectionStatus } from './constants/Constants';

import RuntimeClient from 'runtime-client';
import _ from 'lodash';

function *updateGamepads(interval = 50) {
  while (true) {
    let gamepads = Array.prototype.slice.call(navigator.getGamepads());

    // Windows has a bug where a second, "ghost" gamepad is returned, even when
    // only one is connected. The filter on "mapping" ensures only one gamepad
    // is returned.
    gamepads = _.chain(gamepads)
      .filter((gamepad) => gamepad && gamepad.mapping === 'standard')
      .keyBy('index')
      .mapValues((gamepad) => {
        let inputs = {
          joystick_left_x: gamepad.axes[0],
          joystick_left_y: gamepad.axes[1],
          joystick_right_x: gamepad.axes[2],
          joystick_right_y: gamepad.axes[3],
        };
        let buttons = _.map(gamepad.buttons, (button) => button.pressed);
        for (const [i, button_name] of RuntimeClient.BUTTONS.entries()) {
          inputs[button_name] = buttons[i];
        }
        return inputs;
      })
      .value();

    ipcRenderer.send('sendDatagram', gamepads, '127.0.0.1');  // FIXME
    yield delay(interval);
  }
}

const LATENCY_THRESHOLD = {
  WARNING: 200,
  DISCONNECTED: 1000,
};

function *monitorHealth(points = 5, interval = 200) {
  while (true) {
    let heartbeats = yield select((state) => state.connection.heartbeats);
    if (heartbeats.length > 0) {
      let meanInterval = (new Date() - heartbeats[0]) / heartbeats.length;  // in ms
      if (meanInterval < LATENCY_THRESHOLD.WARNING) {
        yield put(setStatus(ConnectionStatus.HEALTHY));
      } else if (meanInterval < LATENCY_THRESHOLD.DISCONNECTED) {
        yield put(setStatus(ConnectionStatus.WARNING));
      } else {
        yield put(disconnect());
        yield put(setStatus(ConnectionStatus.DISCONNECTED));
      }
    }
    yield delay(interval);
  }
}

function *sendDisconnect() {
   ipcRenderer.send('disconnect');
}

export default function *effects() {
  yield all([
    fork(updateGamepads),
    fork(monitorHealth),
    takeLatest('DISCONNECT', sendDisconnect),
  ]);
}
