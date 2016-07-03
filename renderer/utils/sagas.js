/**
 * Redux sagas are how we handle complicated asynchronous stuff with redux.
 * See http://yelouafi.github.io/redux-saga/index.html for docs.
 * Sagas use ES6 generator functions, which have the '*' in their declaration.
 */

import fs from 'fs';
import { takeEvery, delay } from 'redux-saga';
import { cps, call, put, fork, take, race } from 'redux-saga/effects';
import { remote } from 'electron';
import _ from 'lodash';
import Ansible from './Ansible';

const dialog = remote.dialog;

/**
 * The electron showOpenDialog interface does not work well
 * with redux-saga's 'cps' for callbacks. To make things nicer, we
 * wrap the Electron dialog functionality in a promise,
 * which works well with redux-saga's 'call' for promises.
 *
 * @return {Promise} - fulfilled if user selects file, rejected otherwise
 */
function openFileDialog() {
  return new Promise((resolve, reject) => {
    dialog.showOpenDialog({
      filters: [{ name: 'python', extensions: ['py'] }],
    }, (filepaths) => {
      if (filepaths === undefined) {
        reject();
      } else {
        resolve(filepaths[0]);
      }
    });
  });
}

/**
 * Using Promise for Electron save dialog functionality for the same
 * reason as above.
 *
 * @return {Promise} - fulfilled with filepath once user hits save.
 */
function saveFileDialog() {
  return new Promise((resolve, reject) => {
    dialog.showSaveDialog({
      filters: [{ name: 'python', extensions: ['py'] }],
    }, (filepath) => {
      if (filepath === undefined) {
        reject();
      }

      // Automatically append .py extension if they don't have it
      if (!filepath.endsWith('.py')) {
        resolve(`${filepath}.py`);
      }
      resolve(filepath);
    });
  });
}

function* openFile() {
  const filepath = yield call(openFileDialog);
  const data = yield cps(fs.readFile, filepath, 'utf8');
  yield put({
    type: 'OPEN_FILE_SUCCEEDED',
    code: data,
    filepath,
  });
}

function* saveFile(action) {
  let filepath = action.filepath;
  const code = action.code;
  if (filepath === null) {
    filepath = yield call(saveFileDialog);
  }
  yield cps(fs.writeFile, filepath, code);
  yield put({
    type: 'SAVE_FILE_SUCCEEDED',
    code,
    filepath,
  });
}

/**
 * This saga acts as a "heartbeat" to check whether we are still receiving
 * updates from Runtime.
 *
 * NOTE that this is different from whether or not the Ansible connection
 * is still alive.
 */
function* runtimeHeartbeat() {
  while (true) {
    // Start a race between a delay and receiving an UPDATE_STATUS action from
    // runtime. Only the winner will have a value.
    const result = yield race({
      update: take('UPDATE_STATUS'),
      timeout: call(delay, 1000), // The delay is 1000 ms, or 1 second.
    });

    // If update wins, we assume we are connected, otherwise disconnected.
    if (result.update) {
      yield put({ type: 'RUNTIME_CONNECT' });
    } else {
      yield put({ type: 'RUNTIME_DISCONNECT' });
    }
  }
}

/**
 * This saga removes peripherals that have not been updated by Runtime
 * recently (they are assumed to be disconnected).
 */
function* reapPeripheral(action) {
  const id = action.peripheral.id;
  // Start a race between a delay and receiving an UPDATE_PERIPHERAL action for
  // this same peripheral (per peripheral.id). Only the winner has a value.
  const result = yield race({
    peripheralUpdate: take((nextAction) => (
      nextAction.type === 'UPDATE_PERIPHERAL' && nextAction.peripheral.id === id
    )),
    timeout: call(delay, 3000), // The delay is 3000 ms, or 3 seconds.
  });

  // If the delay won, then we have not received an update for this peripheral
  // recently and remove it from our state.
  if (result.timeout) {
    yield put({ type: 'PERIPHERAL_DISCONNECT', peripheralId: id });
  }
}

const _timestamps = [0, 0, 0, 0];

function _needToUpdate(newGamepads) {
  return _.some(newGamepads, (gamepad, index) => {
    if (!_.isUndefined(gamepad) && (gamepad.timestamp > _timestamps[index])) {
      _timestamps[index] = gamepad.timestamp;
      return true;
    } else if (_.isUndefined(gamepad) && !_.isNull(_timestamps[index])) {
      _timestamps[index] = null;
      return true;
    }
    return false;
  });
}

function _formatGamepadsForJSON(newGamepads) {
  const formattedGamepads = {};
  // Currently there is a bug on windows where navigator.getGamepads()
  // returns a second, 'ghost' gamepad even when only one is connected.
  // The filter on 'mapping' filters out the ghost gamepad.
  _.forEach(_.filter(newGamepads, { mapping: 'standard' }), (gamepad, indexGamepad) => {
    if (gamepad) {
      formattedGamepads[indexGamepad] = {
        index: indexGamepad,
        axes: gamepad.axes,
        buttons: _.map(gamepad.buttons, 'value'),
      };
    }
  });
  return formattedGamepads;
}

/**
 * Repeatedly grab gamepad data, send it over Ansible to the robot, and dispatch
 * redux action to update gamepad state.
 */
function* updateGamepads() {
  while (true) {
    // navigator.getGamepads always returns a reference to the same object. This
    // confuses redux, so we use assignIn to clone to a new object each time.
    const newGamepads = _.assignIn({}, navigator.getGamepads());
    if (_needToUpdate(newGamepads)) {
      // Send gamepad data to Runtime over Ansible.
      if (_.some(newGamepads)) {
        Ansible.sendMessage('gamepad', _formatGamepadsForJSON(newGamepads));
      }

      yield put({ type: 'UPDATE_GAMEPADS', gamepads: newGamepads });
    }

    yield call(delay, 50); // wait 50 ms before updating again.
  }
}

/**
 * The root saga combines all the other sagas together into one.
 */
export default function* rootSaga() {
  yield [
    takeEvery('OPEN_FILE', openFile),
    takeEvery('SAVE_FILE', saveFile),
    takeEvery('UPDATE_PERIPHERAL', reapPeripheral),
    fork(runtimeHeartbeat),
    fork(updateGamepads),
  ];
}
