/**
 * Reducer for editor state data.
 */

const defaultEditorState = {
  filepath: '',
  latestSaveCode: '',
  editorCode: '',
};

const editor = (state = defaultEditorState, action) => {
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
    default:
      return state;
  }
};

export default editor;
