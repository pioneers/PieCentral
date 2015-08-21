import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import AnsibleClient from '../utils/AnsibleClient';
var ActionTypes = Constants.ActionTypes;

function uploadCode(code) {
  AnsibleClient.sendMessage('code', code);
}

var EditorActionCreators = {
  uploadCode(code) {
    uploadCode(code);
    AppDispatcher.dispatch({
      type: ActionTypes.UPLOAD_CODE,
      code: code
    });
  }
};

export default EditorActionCreators;
