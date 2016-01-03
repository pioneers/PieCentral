import AppDispatcher from '../dispatcher/AppDispatcher';
import { ActionTypes } from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';

let editorData = {
  filepath: null,
  latestSaveCode: '',
  editorCode: ''
};

let EditorStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getEditorData() {
    return editorData;
  }
});

function openFile(payload) {
  editorData.latestSaveCode = payload.code;
  // Setting editorCode will be considered a
  // change and will fire an editorUpdate action.
  // We need to wait in order not to conflict with
  // the original getCode dispatch. 
  process.nextTick(() => {
    editorData.editorCode = payload.code;
    editorData.filepath = payload.filepath;
    EditorStore.emitChange();
  });
}

function saveFile(payload) {
  editorData.latestSaveCode = payload.code;
  editorData.filepath = payload.filepath;
  console.log(editorData);
  EditorStore.emitChange();
}

function clearEditor() {
  editorData.latestSaveCode = '';
  editorData.editorCode = '';
  editorData.filepath = null;
  EditorStore.emitChange();
}

function editorUpdate(payload) {
  editorData.editorCode = payload.code;
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
