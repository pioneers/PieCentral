import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
var ActionTypes = Constants.ActionTypes;

var EditorActionCreators = {
  getCode(filename) {
    AppDispatcher
      .get('/api/editor/load?filename=' + filename)
      .then(function(code) {
        AppDispatcher.dispatch({
          type: ActionTypes.GET_CODE,
          success: true,
          code: code
        })
      })
      .catch(function(reason) {
        AppDispatcher.dispatch({
          type: ActionTypes.GET_CODE,
          success: false,
          code: ''
        });
      });
  },
  sendCode(filename, code) {
    AppDispatcher
      .post('/api/editor/save', {filename: filename, code: code})
      .then(function() {
        AppDispatcher.dispatch({
          type: ActionTypes.SEND_CODE,
          success: true,
          code: code
        });
      })
      .catch(function(reason) {
        AppDispatcher.dispatch({
          type: ActionTypes.SEND_CODE,
          success: false,
          code: ''
        });
      })
  }
};

export default EditorActionCreators;
