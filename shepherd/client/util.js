import React from 'react';
import { Button } from '@blueprintjs/core';

const LIGHT_THEME = 'light';
const DARK_THEME = 'dark';

const ThemeToggleButton = props => {
  let themeToggleText, themeToggleIcon;
  if (props.theme === DARK_THEME) {
    themeToggleText = 'Light theme';
    themeToggleIcon = 'flash';
  } else {
    themeToggleText = 'Dark theme';
    themeToggleIcon = 'moon';
  }

  return (
    <Button
      text={themeToggleText}
      icon={themeToggleIcon}
      onClick={props.toggleTheme}
    />
  )
};

const ALLIANCES = {
  BLUE: 'Blue',
  GOLD: 'Gold'
};

export {
  LIGHT_THEME,
  DARK_THEME,
  ThemeToggleButton,
  ALLIANCES
};
