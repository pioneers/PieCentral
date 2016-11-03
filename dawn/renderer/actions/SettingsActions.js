export const increaseFontsize = () => ({
  type: 'INCREASE_FONTSIZE',
});

export const decreaseFontsize = () => ({
  type: 'DECREASE_FONTSIZE',
});

export const changeTheme = (theme) => ({
  type: 'CHANGE_THEME',
  theme,
});
