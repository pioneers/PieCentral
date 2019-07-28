import { createStore, combineReducers } from 'redux';
import { updateTeams as teams } from './team';

export default createStore(combineReducers({ teams }));
