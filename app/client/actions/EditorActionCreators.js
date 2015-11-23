import AppDispatcher from '../dispatcher/AppDispatcher';
import Constants from '../constants/Constants';
import async from '../utils/Async';
var ActionTypes = Constants.ActionTypes;

var EditorActionCreators = {
  getCode(filename) {
    async
      .get('/api/editor/load?filename=' + filename)
      .then(function(code) {
        AppDispatcher.dispatch({
          type: ActionTypes.GET_CODE,
          success: true,
          code: code
        });
      })
      .catch(function(reason) {
        AppDispatcher.dispatch({
          type: ActionTypes.GET_CODE,
          success: false,
          code: null
        });
      });
  },
  sendCode(filename, code) {
    async
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
          code: null
        });
      })
  },
  editorUpdate(newVal) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_EDITOR,
      newCode: newVal
    });
  },
  getFilenames() {
    async.get('/api/editor/list').then(function(data) {
      AppDispatcher.dispatch({
        type: ActionTypes.UPDATE_FILENAMES,
        success: true,
        filenames: JSON.parse(data).filenames
      });
    }).catch(function(reason) {
      console.log(reason);
      AppDispatcher.dispatch({
        type: ActionTypes.UPDATE_FILENAMES,
        success: false,
        filenames: null
      });
    });
  },
  setFilename(filename) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_FILENAME,
      filename: filename
    });
  }
};

export default EditorActionCreators;
