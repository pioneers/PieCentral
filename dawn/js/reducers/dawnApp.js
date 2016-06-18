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

const dawnApp = combineReducers({
  asyncAlerts: asyncAlerts,
  editor: editor,
  studentConsole: studentConsole,
  peripherals: peripherals,
  info: info,
  gamepads: gamepads
});

export default dawnApp;
