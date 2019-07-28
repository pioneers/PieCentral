import { createStore, combineReducers } from 'redux';
import { handleMatchUpdate as match } from './game/match';
import { handleTeamsUpdate as teams } from './game/team';
import { handleThemeToggle as theme } from './util';

export default createStore(combineReducers({ match, teams, theme }));
