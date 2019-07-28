import { createStore, combineReducers } from 'redux';
import { handleTeamsUpdate as teams } from './game/team';
import { handleThemeToggle as theme } from './util';

export default createStore(combineReducers({ teams, theme }));
