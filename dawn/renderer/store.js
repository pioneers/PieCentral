import { compose, createStore, applyMiddleware, combineReducers } from 'redux';
import createSagaMiddleware from 'redux-saga';
import rootSaga from './utils/sagas';

import devices from './reducers/devices';
import preferences from './reducers/preferences';

const sagaMiddleware = createSagaMiddleware();
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
const reducer = combineReducers({
  devices,
  preferences,
});
const store = createStore(
  reducer,
  // composeEnhancers(applyMiddleware(sagaMiddleware)),
);

// sagaMiddleware.run(rootSaga);

export default store;
