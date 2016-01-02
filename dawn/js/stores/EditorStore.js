import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
var ActionTypes = Constants.ActionTypes;

var editorData = {
  filePath: null,
  latestSaveCode: '',
  editorCode: ''
};

var EditorStore = assign({}, EventEmitter.prototype, {
  emitError(err) {
    this.emit('error', err);
  },
  emitChange() {
    this.emit('change');
  },
  getEditorData() {
    return editorData;
  }
});


function receive(type, successful, receivedCode) {
  if(successful) {
    if(type == ActionTypes.SEND_CODE) {
      EditorStore.emitSuccess();
    }
    update(receivedCode);
  } else {
    let error_msg = (type == ActionTypes.SEND_CODE)
      ? 'Failed to save code'
      : 'Failed to receive code';
    EditorStore.emitError(error_msg);
  }
}

function openFile(payload) {
  editorData.latestSaveCode = payload.code;
  // Setting editorCode will be considered a
  // change and will fire an editorUpdate action.
  // We need to wait in order not to conflict with
  // the original getCode dispatch. 
  process.nextTick(() => {
    editorData.editorCode = payload.code;
    editorData.filePath = payload.filePath;
    EditorStore.emitChange();
  });
}

function saveFile(payload) {
  editorData.latestSaveCode = payload.code;
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
    case ActionTypes.UPDATE_EDITOR:
      editorUpdate(action.payload);
      break;
  }
});

export default EditorStore;
