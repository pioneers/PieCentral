import AppDispatcher from '../dispatcher/AppDispatcher';
import { ActionTypes } from '../constants/Constants';
import fs from 'fs';
import { remote } from 'electron';
const dialog = remote.dialog;

let EditorActionCreators = {
  readFilepath(filepath) {
    fs.readFile(filepath, 'utf8', function(err, data) {
      if (err) {
      } else {
        localStorage.setItem('lastFile', filepath);
        AppDispatcher.dispatch({
          type: ActionTypes.OPEN_FILE,
          payload: {
            filepath: filepath,
            code: data
          }
        });
      }
    });
  },
  openFile() {
    dialog.showOpenDialog({
      filters: [{ name: 'python', extensions: ['py']}]
    }, (filepaths) => {
      if (filepaths === undefined) return;
      // Store as lastFile in localStorage. lastFile is auto-opened on startup.
      localStorage.setItem('lastFile', filepaths[0]);
      this.readFilepath(filepaths[0]);
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
      dialog.showSaveDialog({
        filters: [{ name: 'python', extensions: ['py']}]
      }, function(filepath) {
        if (filepath === undefined) return;

        // Automatically append .py extension if they don't have it
        if (filepath.endsWith('.py')) {
          writeContents(filepath);
        } else {
          writeContents(filepath + '.py');
        }
      });
    } else {
      writeContents(filepath);
    }
  },
  createNewFile() {
    localStorage.removeItem('lastFile');
    AppDispatcher.dispatch({
      type: ActionTypes.CLEAR_EDITOR
    });
  },
  deleteFile(filepath) {
    fs.unlink(filepath, function() {
      AppDispatcher.dispatch({
        type: ActionTypes.CLEAR_EDITOR
      });
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
