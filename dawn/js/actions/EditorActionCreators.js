import AppDispatcher from '../dispatcher/AppDispatcher';
import { ActionTypes } from '../constants/Constants';
import fs from 'fs';
import { remote } from 'electron';
const dialog = remote.dialog;

var EditorActionCreators = {
  openFile() {
    dialog.showOpenDialog({
      filters: [{ name: 'python', extensions: ['py']}]
    }, function(filenames) {
      if (filenames.length === undefined) return;
      fs.readFile(filenames[0], 'utf8', function(err, data) {
        if (err) {
          AppDispatcher.dispatch({
            type: ActionTypes.GET_CODE,
            success: false,
            code: null
          });
        } else {
          AppDispatcher.dispatch({
            type: ActionTypes.GET_CODE,
            success: true,
            code: data
          });
        }
      });
    });
  },
  saveFile(filePath, code) {
    fs.writeFile(filePath, code, function(err) {
      if (err) {
        AppDispatcher.dispatch({
          type: ActionTypes.SAVE_CODE,
          success: false,
          code: null
        });
      } else {
        AppDispatcher.dispatch({
          type: ActionTypes.SAVE_CODE,
          success: true,
          code: code
        });
      }
    });
  },
  editorUpdate(newVal) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_EDITOR,
      newCode: newVal
    });
  }
};

export default EditorActionCreators;
