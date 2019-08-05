import { applyMiddleware, createStore, combineReducers } from 'redux';
import promiseMiddleware from 'redux-promise';
import { handleMatchUpdate as match } from './game/match';
import { handleTeamsUpdate as teams } from './game/team';
import { handleResourcesUpdate as resources } from './game/resource';
import { handleThemeToggle as theme } from './util';

const reducer = combineReducers({ match, teams, theme, resources });
export default createStore(reducer, {}, applyMiddleware(promiseMiddleware));
