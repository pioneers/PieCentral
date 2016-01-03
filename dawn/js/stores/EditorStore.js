import AppDispatcher from '../dispatcher/AppDispatcher';
import { ActionTypes } from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';

let _editorData = {
  filepath: null,
  latestSaveCode: '',
  editorCode: ''
};

let EditorStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getFilepath() {
    return _editorData.filepath;
  },
  getLatestSaveCode() {
    return _editorData.latestSaveCode;
  },
  getEditorCode() {
    return _editorData.editorCode;
  }
});

function openFile(payload) {
  _editorData.latestSaveCode = payload.code;
  // Setting editorCode will be considered a
  // change and will fire an editorUpdate action.
  // We need to wait in order not to conflict with
  // the original getCode dispatch. 
  process.nextTick(() => {
    _editorData.editorCode = payload.code;
    _editorData.filepath = payload.filepath;
    EditorStore.emitChange();
  });
}

function saveFile(payload) {
  _editorData.latestSaveCode = payload.code;
  _editorData.filepath = payload.filepath;
  EditorStore.emitChange();
}

function clearEditor() {
  _editorData.latestSaveCode = '';
  _editorData.editorCode = '';
  _editorData.filepath = null;
  EditorStore.emitChange();
}

function editorUpdate(payload) {
  _editorData.editorCode = payload.code;
  EditorStore.emitChange();
}

EditorStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.SAVE_FILE:
      saveFile(action.payload);
      break;
    case ActionTypes.OPEN_FILE:
      openFile(action.payload);
      break;
    case ActionTypes.CLEAR_EDITOR:
      clearEditor();
      break;
    case ActionTypes.UPDATE_EDITOR:
      editorUpdate(action.payload);
      break;
  }
});

export default EditorStore;
