/**
 * Actions for the editor state.
 */

export const editorUpdate = newVal => ({
  type: 'UPDATE_EDITOR',
  code: newVal,
});

export const openFileSucceeded = (data, filepath) => ({
  type: 'OPEN_FILE_SUCCEEDED',
  code: data,
  filepath,
});

export const saveFileSucceeded = (data, filepath) => ({
  type: 'SAVE_FILE_SUCCEEDED',
  code: data,
  filepath,
});

export const openFile = () => ({
  type: 'OPEN_FILE',
});

export const saveFile = (saveAs = false) => ({
  type: 'SAVE_FILE',
  saveAs,
});

export const deleteFile = () => ({
  type: 'DELETE_FILE',
});

export const createNewFile = () => ({
  type: 'CREATE_NEW_FILE',
});

export const downloadCode = () => ({
  type: 'DOWNLOAD_CODE',
});
