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
    process.nextTick(() => this.emit('change'));
    //this.emit('change');
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
  editorData.latestSaveCode = receivedCode;
  EditorStore.emitChange();
  setTimeout(function(){
    editorData.editorCode = receivedCode;
    EditorStore.emitChange();
  }, 1);
}

function sendCodeUpdate(success, sentCode) {
  editorData.latestSaveCode = sentCode;
  EditorStore.emitChange();
}

function editorUpdate(newCode) {
  editorData.editorCode = newCode;
  EditorStore.emitChange();
}

EditorStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.SEND_CODE:
      sendCodeUpdate(action.success, action.code);
    case ActionTypes.GET_CODE:
      getCodeUpdate(action.success, action.code);
    case ActionTypes.UPDATE_EDITOR:
      editorUpdate(action.newCode);
  }
});

export default EditorStore;
