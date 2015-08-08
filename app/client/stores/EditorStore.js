import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import {EventEmitter} from 'events';
import assign from 'object-assign';
var ActionTypes = Constants.ActionTypes;

var code = '';
var EditorStore = assign({}, EventEmitter.prototype, {
  emitChange() {
    this.emit('change');
  },
  getCode() {
    return code;
  }
});

function update(receivedCode) {
  code = receivedCode;
  EditorStore.emitChange();
}

EditorStore.dispatchToken = AppDispatcher.register((action) => {
  switch (action.type) {
    case ActionTypes.UPLOAD_CODE:
      update(action.code);
  }
});

export default EditorStore;
