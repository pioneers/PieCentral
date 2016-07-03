/**
 * Combining all the reducers into one and exporting it.
 */

import { combineReducers } from 'redux';

import asyncAlerts from './alerts';
import editor from './editor';
import studentConsole from './studentConsole';
import peripherals from './peripherals';
import info from './info';
import gamepads from './gamepads';
import settings from './settings';

const dawnApp = combineReducers({
  asyncAlerts,
  editor,
  studentConsole,
  peripherals,
  info,
  gamepads,
  settings,
});

export default dawnApp;
