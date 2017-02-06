import 'babel-polyfill';
import fs from 'fs';
import { assert } from 'chai';
import { delay } from 'redux-saga';
import { call, take } from 'redux-saga/effects';
// import { remote } from 'electron';
import { openFileSucceeded, saveFileSucceeded } from '../../actions/EditorActions';
import { runtimeConnect, runtimeDisconnect } from '../../actions/InfoActions';
import { peripheralDisconnect } from '../../actions/PeripheralActions';
import { openFileDialog,
         unsavedDialog,
         openFile,
         writeFile,
         editorState,
         editorSavedState,
         saveFileDialog,
         saveFile,
         runtimeHeartbeat,
         actionWithSamePeripheral,
         reapPeripheral,
         gamepadsState,
         updateMainProcess,
         ansibleReceiver,
         ansibleSaga } from '../sagas';
import fromGenerator from './redux-saga-test';

describe('filesystem sagas', () => {
  it('should yield effects for opening file (unsaved)', () => {
    const action = {
      type: 'OPEN_FILE',
    };
    const type = 'open';
    const expect = fromGenerator(assert, openFile(action));
    expect.next().select(editorSavedState);
    expect.next({
      savedCode: 'this was last code saved',
      code: 'this is new modifications after last save',
    }).call(unsavedDialog, type);
    expect.next(1).call(openFileDialog);
    expect.next('mock-path').cps(fs.readFile, 'mock-path', 'utf8');
    expect.next('mock-data').put(openFileSucceeded('mock-data', 'mock-path'));
    expect.next().returns();
  });

  it('should yield effects for creating new file (unsaved)', () => {
    const action = {
      type: 'CREATE_NEW_FILE',
    };
    const type = 'create';
    const expect = fromGenerator(assert, openFile(action));
    expect.next().select(editorSavedState);
    expect.next({
      savedCode: 'this was last code saved',
      code: 'this is new modifications after last save',
    }).call(unsavedDialog, type);
    expect.next(1).put(openFileSucceeded('', null));
    expect.next().returns();
  });

  it('should yield effects for writing file', () => {
    const expect = fromGenerator(assert, writeFile('mock-path', 'mock-code'));
    expect.next().cps(fs.writeFile, 'mock-path', 'mock-code');
    expect.next().put(saveFileSucceeded('mock-code', 'mock-path'));
    expect.next().returns();
  });

  it('should yield effects for saving file', () => {
    const action = {
      type: 'SAVE_FILE',
      saveAs: false,
    };
    const expect = fromGenerator(assert, saveFile(action));
    expect.next().select(editorState);
    // follows to writeFile
    expect.next({
      filepath: 'mock-path',
      code: 'mock-code',
    }).cps(fs.writeFile, 'mock-path', 'mock-code');
  });

  it('should yield effects for saving file as (saveAs true)', () => {
    const action = {
      type: 'SAVE_FILE',
      saveAs: true,
    };
    const expect = fromGenerator(assert, saveFile(action));
    expect.next().select(editorState);
    expect.next({
      filepath: 'mock-path',
      code: 'mock-code',
    }).call(saveFileDialog);
    // follows to writeFile
    expect.next('mock-new-path').cps(fs.writeFile, 'mock-new-path', 'mock-code');
  });

  it('should yield effects for saving file as (no filepath)', () => {
    const action = {
      type: 'SAVE_FILE',
      saveAs: false,
    };
    const expect = fromGenerator(assert, saveFile(action));
    expect.next().select(editorState);
    expect.next({
      filepath: null,
      code: 'mock-code',
    }).call(saveFileDialog);
    // follows to writeFile
    expect.next('mock-path').cps(fs.writeFile, 'mock-path', 'mock-code');
  });
});

describe('runtime sagas', () => {
  it('should yield effects for runtime heartbeat, connected', () => {
    const expect = fromGenerator(assert, runtimeHeartbeat());
    expect.next().race({
      update: take('UPDATE_STATUS'),
      timeout: call(delay, 1000),
    });
    expect.next({
      update: {
        type: 'UPDATE_STATUS',
      },
    }).put(runtimeConnect());
  });

  it('should yield effects for runtime heartbeat, disconnected', () => {
    const expect = fromGenerator(assert, runtimeHeartbeat());
    expect.next().race({
      update: take('UPDATE_STATUS'),
      timeout: call(delay, 1000),
    });
    expect.next({
      timeout: 1000,
    }).put(runtimeDisconnect());
  });

  it('should yield effects to reap peripheral, no timeout', () => {
    const action = {
      type: 'UPDATE_PERIPHERAL',
      peripheral: {
        device_type: 'SENSOR_SCALAR',
        device_name: 'SS1',
        value: 50,
        uid: {
          low: 123,
          high: 456,
        },
      },
    };
    const expect = fromGenerator(assert, reapPeripheral(action));
    expect.next().race({
      peripheralUpdate: take(actionWithSamePeripheral),
      timeout: call(delay, 3000),
    });
    expect.next({
      peripheralUpdate: action,
    }).returns();
  });

  it('should yield effects to reap peripheral, timeout', () => {
    const action = {
      type: 'UPDATE_PERIPHERAL',
      peripheral: {
        device_type: 'SENSOR_SCALAR',
        device_name: 'SS1',
        value: 50,
        uid: {
          low: 123,
          high: 456,
        },
      },
    };
    const expect = fromGenerator(assert, reapPeripheral(action));
    expect.next().race({
      peripheralUpdate: take(actionWithSamePeripheral),
      timeout: call(delay, 3000),
    });
    expect.next({
      timeout: 3000,
    }).put(peripheralDisconnect('456123'));
    expect.next().returns();
  });

  it('should update main process of store changes', () => {
    const expect = fromGenerator(assert, updateMainProcess());
    expect.next().select(gamepadsState);
  });

  it('should take data from ansibleReceiver and dispatch to store', () => {
    const expect = fromGenerator(assert, ansibleSaga());
    expect.next().call(ansibleReceiver);
    /* cannot test ipcRenderer for is undefined in test env
    const chan = ansibleReceiver();
    expect.next(chan).take(chan);
    expect.next({
      type: "SOME_ACTION"
    }).put({
      type: "SOME_ACTION"
    })*/
  });
});
