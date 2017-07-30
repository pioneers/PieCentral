import fs from 'fs';
import { assert } from 'chai';
import { delay } from 'redux-saga';
import { call, take } from 'redux-saga/effects';
// import { remote } from 'electron';
import { openFileSucceeded, saveFileSucceeded } from '../../actions/EditorActions';
import { runtimeConnect, runtimeDisconnect } from '../../actions/InfoActions';
import {
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
} from '../sagas';
import fromGenerator from './redux-saga-test';
import { TIMEOUT } from '../../utils/utils';

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
      update: take('PER_MESSAGE'),
      timeout: call(delay, TIMEOUT),
    });
    expect.next({
      update: {
        type: 'PER_MESSAGE',
      },
    }).put(runtimeConnect());
  });

  it('should yield effects for runtime heartbeat, disconnected', () => {
    const expect = fromGenerator(assert, runtimeHeartbeat());
    expect.next().race({
      update: take('PER_MESSAGE'),
      timeout: call(delay, TIMEOUT),
    });
    expect.next({
      timeout: TIMEOUT,
    }).put(runtimeDisconnect());
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
    }) */
  });
});
