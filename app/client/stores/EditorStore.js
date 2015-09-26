import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
var ActionTypes = Constants.ActionTypes;

//TODO: make filename not hard-coded in
var editorData = {
  filename: 'student_code.py',
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

function getCodeUpdate(success, receivedCode) {
  if (success) {
    editorData.latestSaveCode = receivedCode;
    // Setting editorCode will be considered a
    // change and will fire an editorUpdate action.
    // We need to wait in order not to conflict with
    // the original getCode dispatch. Hacky.
    process.nextTick(() => {
      editorData.editorCode = receivedCode;
      EditorStore.emitChange();
    });
  } else {
    EditorStore.emitError('Failed to load code');
  }
}

function sendCodeUpdate(success, sentCode) {
  if (success) {
    editorData.latestSaveCode = sentCode;
    EditorStore.emitChange();
  } else {
    EditorStore.emitError('Failed to save code.');
  }
}

function editorUpdate(newCode) {
  editorData.editorCode = newCode;
  EditorStore.emitChange();
}

EditorStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.SEND_CODE:
      sendCodeUpdate(action.success, action.code);
      break;
    case ActionTypes.GET_CODE:
      getCodeUpdate(action.success, action.code);
      break;
    case ActionTypes.UPDATE_EDITOR:
      editorUpdate(action.newCode);
      break;
  }
});

export default EditorStore;
