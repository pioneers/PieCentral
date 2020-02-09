const DEFAULT_PREFERENCES = {
  darkTheme: true,
  editor: {
    textSize: 12,
  },
};

const preferences = (state = DEFAULT_PREFERENCES, action) => {
  switch (action.type) {
    case 'TOGGLE_DARK_THEME':
      return {...state, darkTheme: !state.darkTheme};
    default:
      return state;
  }
};

export default preferences;
