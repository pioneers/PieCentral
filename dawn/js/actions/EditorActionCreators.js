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
              filepath: filepaths[0],
              code: data
            }
          });
        }
      });
    });
  },
  saveFile(filepath, code) {
    function writeContents(filepath) {
      fs.writeFile(filepath, code, function(err) {
        if (err) {
          console.log(err);
        } else {
          AppDispatcher.dispatch({
            type: ActionTypes.SAVE_FILE,
            payload: {
              code: code,
              filepath: filepath
            }
          });
        }
      });
    };

    if (filepath === null) {
      dialog.showSaveDialog(function(filepath) {
        if (filepath === undefined) return;
        writeContents(filepath);
      });
    } else {
      writeContents(filepath);
    }
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
