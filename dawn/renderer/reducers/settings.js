const initialState = {
  fontSize: 14,
  editorTheme: 'github',
};

const settings = (state = initialState, action) => {
  let fontSize;
  switch (action.type) {
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
