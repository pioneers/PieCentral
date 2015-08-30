import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import AnsibleClient from '../utils/AnsibleClient';
import Api from '../utils/API';
var ActionTypes = Constants.ActionTypes;

function uploadCode(code) {
  AnsibleClient.sendMessage('code', code);
}

var EditorActionCreators = {
  getCode(filename) {
    Api
      .get('/api/editor/load?filename=' + filename)
      .then(function(code){
        AppDispatcher.dispatch({
          type: ActionTypes.RECEIVE_CODE,
          success: true,
          code: code
        })
      })
      .catch(function(reason){
        AppDispatcher.dispatch({
          type: ActionTypes.RECEIVE_CODE,
          success: false,
          code: ''
        });
      });
  },
  uploadCode(code) {
    uploadCode(code);
    AppDispatcher.dispatch({
      type: ActionTypes.SEND_CODE,
      code: code
    });
  }
};

export default EditorActionCreators;
