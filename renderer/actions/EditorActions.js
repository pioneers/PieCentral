/**
 * Actions for the editor state.
 */

export const openFile = () => ({
  type: 'OPEN_FILE',
});

export const saveFile = (filepath, code) => ({
  type: 'SAVE_FILE',
  code,
  filepath,
});

export const deleteFile = () => ({
  type: 'DELETE_FILE',
});

export const createNewFile = () => ({
  type: 'CREATE_NEW_FILE',
});

export const editorUpdate = (newVal) => ({
  type: 'UPDATE_EDITOR',
  code: newVal,
});

export const changeTheme = (theme) => ({
  type: 'CHANGE_THEME',
  theme,
});

export const increaseFontsize = () => ({
  type: 'INCREASE_FONTSIZE',
});

export const decreaseFontsize = () => ({
  type: 'DECREASE_FONTSIZE',
});
