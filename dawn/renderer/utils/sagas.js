/**
 * Redux sagas are how we handle complicated asynchronous stuff with redux.
 * See http://yelouafi.github.io/redux-saga/index.html for docs.
 * Sagas use ES6 generator functions, which have the '*' in their declaration.
 */

import fs from 'fs';
import _ from 'lodash';
import { delay, eventChannel } from 'redux-saga';
import { call, cps, fork, put, race, select, take, takeEvery } from 'redux-saga/effects';
import { ipcRenderer, remote } from 'electron';
import { addAsyncAlert } from '../actions/AlertActions';
import { openFileSucceeded, saveFileSucceeded } from '../actions/EditorActions';
import { toggleFieldControl } from '../actions/FieldActions';
import { updateGamepads } from '../actions/GamepadsActions';
import { runtimeConnect, runtimeDisconnect } from '../actions/InfoActions';
import { TIMEOUT, defaults, logging } from '../utils/utils';


const Client = require('ssh2').Client;

let timestamp = Date.now();

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
    remote.dialog.showOpenDialog({
      filters: [{ name: 'python', extensions: ['py'] }],
    }, (filepaths) => {
      // If filepaths is undefined, the user did not specify a file.
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
    remote.dialog.showSaveDialog({
      filters: [{ name: 'python', extensions: ['py'] }],
    }, (filepath) => {
      // If filepath is undefined, the user did not specify a file.
      if (filepath === undefined) {
        reject();
        return;
      }

      // Automatically append .py extension if they don't have it
      if (!filepath.endsWith('.py')) {
        resolve(`${filepath}.py`);
      }
      resolve(filepath);
    });
  });
}

/**
 * Using Promise for Electron message dialog functionality for the same
 * reason as above.
 *
 * @return {Promise} - fulfilled with button index.
 */
function unsavedDialog(action) {
  return new Promise((resolve, reject) => {
    remote.dialog.showMessageBox({
      type: 'warning',
      buttons: [`Save and ${action}`, `Discard and ${action}`, 'Cancel action'],
      title: 'You have unsaved changes!',
      message: `You are trying to ${action} a new file, but you have unsaved changes to
your current one. What do you want to do?`,
    }, (res) => {
      // 'res' is an integer corrseponding to index in button list above.
      if (res === 0 || res === 1 || res === 2) {
        resolve(res);
      } else {
        reject();
      }
    });
  });
}

/**
 * Simple helper function to write to a codefile and dispatch action
 * notifying store of the save.
 */
function* writeFile(filepath, code) {
  yield cps(fs.writeFile, filepath, code);
  yield put(saveFileSucceeded(code, filepath));
}

const editorState = state => ({
  filepath: state.editor.filepath,
  code: state.editor.editorCode,
});

function* saveFile(action) {
  const result = yield select(editorState);
  let filepath = result.filepath;
  const code = result.code;
  // If the action is a "save as" OR there is no filepath (ie, a new file)
  // then we open the save file dialog so the user can specify a filename before saving.
  if (action.saveAs === true || !filepath) {
    try {
      filepath = yield call(saveFileDialog);
      yield* writeFile(filepath, code);
    } catch (e) {
      logging.log('No filename specified, file not saved.');
    }
  } else {
    yield* writeFile(filepath, code);
  }
}

const editorSavedState = state => ({
  savedCode: state.editor.latestSaveCode,
  code: state.editor.editorCode,
});

function* openFile(action) {
  const type = (action.type === 'OPEN_FILE') ? 'open' : 'create';
  const result = yield select(editorSavedState);
  let res = 1;
  if (result.code !== result.savedCode) {
    res = yield call(unsavedDialog, type);
    if (res === 0) {
      yield* saveFile({
        type: 'SAVE_FILE',
        saveAs: false,
      });
    }
  }
  if (res === 0 || res === 1) {
    if (type === 'open') {
      try {
        const filepath = yield call(openFileDialog);
        const data = yield cps(fs.readFile, filepath, 'utf8');
        yield put(openFileSucceeded(data, filepath));
      } catch (e) {
        logging.log('No filename specified, no file opened.');
      }
    } else if (type === 'create') {
      yield put(openFileSucceeded('', null));
    }
  } else {
    logging.log(`File ${type} canceled.`);
  }
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
      update: take('PER_MESSAGE'),
      timeout: call(delay, TIMEOUT),
    });

    // If update wins, we assume we are connected, otherwise disconnected.
    if (result.update) {
      yield put(runtimeConnect());
    } else {
      yield put(runtimeDisconnect());
    }
  }
}

const _timestamps = [0, 0, 0, 0];

function _needToUpdate(newGamepads) {
  return _.some(newGamepads, (gamepad, index) => {
    if (gamepad != null && (gamepad.timestamp > _timestamps[index])) {
      _timestamps[index] = gamepad.timestamp;
      return true;
    } else if (gamepad == null && _timestamps[index] != null) {
      _timestamps[index] = null;
      return true;
    }
    return false;
  });
}

function formatGamepads(newGamepads) {
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
function* ansibleGamepads() {
  while (true) {
    // navigator.getGamepads always returns a reference to the same object. This
    // confuses redux, so we use assignIn to clone to a new object each time.
    const newGamepads = Array.prototype.slice.call(navigator.getGamepads());
    if (_needToUpdate(newGamepads) || Date.now() - timestamp > 100) {
      const formattedGamepads = formatGamepads(newGamepads);
      yield put(updateGamepads(formattedGamepads));

      // Send gamepad data to Runtime over Ansible.
      if (_.some(newGamepads) || Date.now() - timestamp > 100) {
        timestamp = Date.now();
        yield put({ type: 'UPDATE_MAIN_PROCESS' });
      }
    }

    yield call(delay, 50); // wait 50 ms before updating again.
  }
}

/**
 * Creates the ansibleReceiver eventChannel, which emits
 * data received from the main process.
 */
function ansibleReceiver() {
  return eventChannel((emitter) => {
    const listener = (event, action) => {
      emitter(action);
    };
    // Suscribe listener to dispatches from main process.
    ipcRenderer.on('dispatch', listener);
    // Return an unsuscribe function.
    return () => {
      ipcRenderer.removeListener('dispatch', listener);
    };
  });
}

/**
 * Takes data from the ansibleReceiver channel and dispatches
 * it to the store
 */
function* ansibleSaga() {
  try {
    const chan = yield call(ansibleReceiver);
    while (true) {
      const action = yield take(chan);
      // dispatch the action
      yield put(action);
    }
  } catch (e) {
    logging.log(e.stack);
  }
}

const gamepadsState = state => ({
  studentCodeStatus: state.info.studentCodeStatus,
  gamepads: state.gamepads.gamepads,
});

const lcmState = state => ({
  connectionStatus: state.info.connectionStatus,
  runtimeStatus: state.info.runtimeStatus,
});

/**
 * Send the store to the main process whenever it changes.
 */
function* updateMainProcess() {
  const stateSlice = yield select(gamepadsState);
  ipcRenderer.send('stateUpdate', stateSlice);
  const lcmSlice = yield select(lcmState);
  ipcRenderer.send('LCM_STATUS_UPDATE', lcmSlice);
}

function* restartRuntime() {
  const conn = new Client();
  const stateSlice = yield select(state => ({
    runtimeStatus: state.info.runtimeStatus,
    ipAddress: state.info.ipAddress,
  }));
  if (stateSlice.runtimeStatus && stateSlice.ipAddress !== defaults.IPADDRESS) {
    const network = yield call(() => new Promise((resolve) => {
      conn.on('ready', () => {
        conn.exec('sudo systemctl restart runtime.service',
          { pty: true }, (uperr, stream) => {
            if (uperr) {
              resolve(1);
            }
            stream.write(`${defaults.PASSWORD}\n`);
            stream.on('exit', (code) => {
              logging.log(`Runtime Restart: Returned ${code}`);
              conn.end();
              resolve(0);
            });
          });
      }).connect({
        debug: (inpt) => {
          logging.log(inpt);
        },
        host: stateSlice.ipAddress,
        port: defaults.PORT,
        username: defaults.USERNAME,
        password: defaults.PASSWORD,
      });
    }));
    if (network === 1) {
      yield addAsyncAlert(
        'Runtime Restart Error',
        'Dawn was unable to run restart commands. Please check your robot connectivity.',
      );
    }
  }
}

function* downloadStudentCode() {
  const conn = new Client();
  const stateSlice = yield select(state => ({
    runtimeStatus: state.info.runtimeStatus,
    ipAddress: state.info.ipAddress,
  }));
  const path = `${require('electron').remote.app.getPath('desktop')}/Dawn`; // eslint-disable-line global-require
  try {
    fs.statSync(path);
  } catch (fileErr) {
    fs.mkdirSync(path);
  }
  if (stateSlice.runtimeStatus && stateSlice.ipAddress !== defaults.IPADDRESS) {
    const errors = yield call(() => new Promise((resolve) => {
      conn.on('ready', () => {
        conn.sftp((err, sftp) => {
          if (err) resolve(1);
          sftp.fastGet('./PieCentral/runtime/studentCode.py', `${path}/robotCode.py`,
            { step: (totalTransferred, chunk, total) => {
              if (totalTransferred === total) {
                resolve(0);
              }
            },
            },
            (err2) => {
              logging.log(err2);
              resolve(2);
            });
        });
      }).connect({
        debug: (inpt) => {
          logging.log(inpt);
        },
        host: stateSlice.ipAddress,
        port: defaults.PORT,
        username: defaults.USERNAME,
        password: defaults.PASSWORD,
      });
    }));
    switch (errors) {
      case 0: {
        const data = yield cps(fs.readFile, `${path}/robotCode.py`, 'utf8');
        yield put(openFileSucceeded(data, `${path}/robotCode.py`));
        logging.log('Succeeded in Download');
        break;
      }
      case 1: {
        yield addAsyncAlert('Robot File Download Error',
          'Dawn was unable to connect to the robot for file download.',
        );
        break;
      }
      case 2: {
        yield addAsyncAlert('Robot File Download Error',
          'Dawn was unable to download student code fully.',
        );
        break;
      }
      default: {
        yield addAsyncAlert('Robot File Download Error',
          'Dawn was unable to download student code due to some unknown error.',
        );
        break;
      }
    }
  }
}

function* tcpConfirmation() {
  const result = yield race({
    update: take('NOTIFICATION_RECEIVED'),
    timeout: call(delay, TIMEOUT), // The delay is 5000 ms, or 5 second.
  });

  if (!result.update) {
    this.logger.log('Runtime failed to confirm');
    yield addAsyncAlert('Upload Issue',
      'Runtime Unresponsive',
    );
  } else {
    const stateSlice = yield select(state => ({
      ipAddress: state.info.ipAddress,
      filepath: state.editor.filepath,
    }));
    const conn = new Client();
    const errors = yield call(() => new Promise((resolve) => {
      conn.on('error', (err) => {
        logging.log(err);
        resolve(3);
      });

      conn.on('ready', () => {
        conn.sftp((err, sftp) => {
          if (err) {
            logging.log(err);
            resolve(1);
          }
          sftp.fastPut(stateSlice.filepath, './PieCentral/runtime/studentCode.py',
            {
              step: (totalTransferred, chunk, total) => {
                if (totalTransferred === total) {
                  resolve(0);
                }
              },
            },
            (err2) => {
              if (err2) {
                logging.log(err2);
                resolve(2);
              }
            });
        });
      }).connect({
        debug: (input) => {
          logging.log(input);
        },
        host: stateSlice.ipAddress,
        port: defaults.PORT,
        username: defaults.USERNAME,
        password: defaults.PASSWORD,
      });
    }));

    switch (errors) {
      case 0: {
        yield addAsyncAlert('Upload Success',
          'File Uploaded Successfully',
        );
        break;
      }
      case 1: {
        yield addAsyncAlert('Upload Issue',
          'SFTP session could not be initiated',
        );
        break;
      }
      case 2: {
        yield addAsyncAlert('Upload Issue',
          'File failed to be transmitted',
        );
        break;
      }
      case 3: {
        yield addAsyncAlert('Upload Issue',
          'Robot could not be connected.',
        );
        break;
      }
      default: {
        yield addAsyncAlert('Upload Issue',
          'Unknown Error',
        );
        break;
      }
    }
    setTimeout(() => {
      conn.end();
    }, 50);
  }
}

function* handleFieldControl() {
  const stateSlice = yield select(state => ({
    fieldControlStatus: state.fieldStore.fieldControl,
  }));
  if (stateSlice.fieldControlStatus) {
    yield put(toggleFieldControl(false));
    ipcRenderer.send('LCM_TEARDOWN');
  } else {
    yield put(toggleFieldControl(true));
    ipcRenderer.send('LCM_INITIALIZE');
  }
}


/**
 * The root saga combines all the other sagas together into one.
 */
export default function* rootSaga() {
  yield [
    takeEvery('OPEN_FILE', openFile),
    takeEvery('SAVE_FILE', saveFile),
    takeEvery('CREATE_NEW_FILE', openFile),
    takeEvery('UPDATE_MAIN_PROCESS', updateMainProcess),
    takeEvery('RESTART_RUNTIME', restartRuntime),
    takeEvery('DOWNLOAD_CODE', downloadStudentCode),
    takeEvery('NOTIFICATION_SENT', tcpConfirmation),
    takeEvery('TOGGLE_FIELD_CONTROL', handleFieldControl),
    fork(runtimeHeartbeat),
    fork(ansibleGamepads),
    fork(ansibleSaga),
  ];
}

export {
  openFileDialog,
  unsavedDialog,
  openFile,
  writeFile,
  editorState,
  editorSavedState,
  saveFileDialog,
  saveFile,
  runtimeHeartbeat,
  gamepadsState,
  updateMainProcess,
  ansibleReceiver,
  ansibleSaga,
}; // for tests
