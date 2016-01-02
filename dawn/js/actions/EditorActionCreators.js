import AppDispatcher from '../dispatcher/AppDispatcher';
import { ActionTypes } from '../constants/Constants';
import fs from 'fs';
import { remote } from 'electron';
const dialog = remote.dialog;

var EditorActionCreators = {
  openFile() {
    dialog.showOpenDialog({
      filters: [{ name: 'python', extensions: ['py']}]
    }, function(filepaths) {
      if (filepaths === undefined) return;
      fs.readFile(filepaths[0], 'utf8', function(err, data) {
        if (err) {
          console.log('error');
        } else {
          AppDispatcher.dispatch({
            type: ActionTypes.OPEN_FILE,
            payload: {
              filePath: filepaths[0],
              code: data
            }
          });
        }
      });
    });
  },
  saveFile(filePath, code) {
    fs.writeFile(filePath, code, function(err) {
      if (err) {
        console.log(err);
      } else {
        AppDispatcher.dispatch({
          type: ActionTypes.SAVE_CODE,
          payload: {
            code: code
          }
        });
      }
    });
  },
  editorUpdate(newVal) {
    AppDispatcher.dispatch({
      type: ActionTypes.UPDATE_EDITOR,
      payload: {
        code: newVal
      }
    });
  }
};

export default EditorActionCreators;
