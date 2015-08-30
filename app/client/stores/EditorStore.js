import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
var ActionTypes = Constants.ActionTypes;

var code = '';
var EditorStore = assign({}, EventEmitter.prototype, {
  emitLoadError() {
    this.emit('loadError');
  },
  emitChange() {
    this.emit('change');
  },
  getCode() {
    return code;
  }
});


function receive(successful, receivedCode) {
  if(successful) {
    update(receivedCode);
  } else {
    EditorStore.emitLoadError();
  }
}

function update(receivedCode) {
  code = receivedCode;
  EditorStore.emitChange();
}

EditorStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.SEND_CODE:
      update(action.code);
    case ActionTypes.RECEIVE_CODE:
      receive(action.success, action.code);
  }
});

export default EditorStore;
