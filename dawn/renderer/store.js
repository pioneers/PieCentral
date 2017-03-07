import { compose, createStore, applyMiddleware } from 'redux';
import createSagaMiddleware from 'redux-saga';
import dawnApp from './reducers/dawnApp';
import rootSaga from './utils/sagas';

const sagaMiddleware = createSagaMiddleware();

const store = createStore(
  dawnApp,
  compose(
    applyMiddleware(sagaMiddleware),
  ),
);

sagaMiddleware.run(rootSaga);

export default store;
