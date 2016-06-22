/**
 * Reducer for editor state data.
 */

const defaultEditorState = {
  showConsole: false,
  filepath: null,
  latestSaveCode: '',
  editorCode: '',
  editorTheme: 'github',
  fontSize: 14,
};

const editor = (state = defaultEditorState, action) => {
  let fontSize;
  switch (action.type) {
    case 'UPDATE_EDITOR':
      return {
        ...state,
        editorCode: action.code,
      };
    case 'OPEN_FILE_SUCCEEDED':
      return {
        ...state,
        editorCode: action.code,
        filepath: action.filepath,
        latestSaveCode: action.code,
      };
    case 'SAVE_FILE_SUCCEEDED':
      return {
        ...state,
        filepath: action.filepath,
        latestSaveCode: action.code,
      };
    case 'CHANGE_THEME':
      return {
        ...state,
        editorTheme: action.theme,
      };
    case 'CREATE_NEW_FILE':
      return {
        ...state,
        filepath: null,
        editorCode: '',
        latestSaveCode: '',
      };
    case 'INCREASE_FONTSIZE':
      fontSize = state.fontSize;
      return {
        ...state,
        fontSize: (fontSize <= 28) ? fontSize + 1 : fontSize,
      };
    case 'DECREASE_FONTSIZE':
      fontSize = state.fontSize;
      return {
        ...state,
        fontSize: (fontSize >= 8) ? fontSize - 1 : fontSize,
      };
    default:
      return state;
  }
};

export default editor;
