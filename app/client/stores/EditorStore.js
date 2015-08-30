import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
var ActionTypes = Constants.ActionTypes;

//TODO: make filename not hard-coded in
var file = {filename: 'student_code.py', code: ''};
var EditorStore = assign({}, EventEmitter.prototype, {
  emitError(err) {
    this.emit('error', err);
  },
  emitSuccess() {
    this.emit('success');
  },
  emitChange() {
    this.emit('change');
  },
  getFile() {
    return file;
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

function update(receivedCode) {
  file.code = receivedCode;
  EditorStore.emitChange();
}

EditorStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.SEND_CODE:
    case ActionTypes.GET_CODE:
      receive(action.type, action.success, action.code);
  }
});

export default EditorStore;
