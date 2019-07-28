import { createStore, combineReducers } from 'redux';
import { handleTeamsUpdate as teams } from './team';
import { handleThemeToggle as theme } from './util';

export default createStore(combineReducers({ teams, theme }));
