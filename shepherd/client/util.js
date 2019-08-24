import React from 'react';
import { connect } from 'react-redux';
import { Button } from '@blueprintjs/core';

export const LIGHT_THEME = 'light';
export const DARK_THEME = 'dark';

const TOGGLE_THEME = 'TOGGLE_THEME';
const toggleTheme = () => ({ type: TOGGLE_THEME });

export function handleThemeToggle(theme = DARK_THEME, { type }) {
  if (type === TOGGLE_THEME) {
    return theme === LIGHT_THEME ? DARK_THEME : LIGHT_THEME;
  }
  return theme;
}

export const ThemeToggleButton = connect(
  state => ({ theme: state.theme }),
  { toggleTheme }
)(props => {
  let styling;
  if (props.theme === DARK_THEME) {
    styling = { text: 'Light theme', icon: 'flash' };
  } else {
    styling = { text: 'Dark theme', icon: 'moon' };
  }
  return <Button {...styling} onClick={props.toggleTheme} />;
});

export const ALLIANCES = {
  BLUE: 'Blue',
  GOLD: 'Gold',
};

export const MODES = {
  IDLE: 'Idle',
  AUTO: 'Autonomous',
  TELEOP: 'Tele-op',
};

export const RESOURCE_TYPE = {
  ROBOT: 'Robot',
  ARDUINO: 'Arduino',
};

export const RESOURCE_STATUS = {
  OK: 'OK',
  WARNING: 'Warning',
  FAILURE: 'Failure',
};

export const toOptions =
  pairs => Object.entries(pairs).map(([value, label]) => ({ value, label }));
