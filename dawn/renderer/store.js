import { ipcRenderer } from 'electron';
import { compose, createStore, applyMiddleware, combineReducers } from 'redux';
import createSagaMiddleware from 'redux-saga';
import effects from './effects';

import console from './reducers/console';
import connection from './reducers/connection';
import devices from './reducers/devices';
import preferences from './reducers/preferences';

const sagaMiddleware = createSagaMiddleware();
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

const reducer = combineReducers({
  console,
  connection,
  devices,
  preferences,
});

const store = createStore(
  reducer,
  composeEnhancers(applyMiddleware(sagaMiddleware)),
);

ipcRenderer.on('dispatch', (event, action) => {
  store.dispatch(action);
});

sagaMiddleware.run(effects);

export default store;
