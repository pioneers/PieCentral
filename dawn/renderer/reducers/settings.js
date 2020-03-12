const initialState = {
  fontSize: 14,
  editorTheme: 'tomorrow',
};

const settings = (state = initialState, action) => {
  switch (action.type) {
    case 'CHANGE_FONTSIZE':
      return {
        ...state,
        fontSize: action.newFontsize,
      };
    case 'CHANGE_THEME':
      return {
        ...state,
        editorTheme: action.theme,
      };
    default:
      return state;
  }
};

export default settings;
