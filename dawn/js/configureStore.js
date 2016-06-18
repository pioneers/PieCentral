import dawnApp from './reducers/dawnApp';
import { compose, createStore, applyMiddleware } from 'redux';
import createSagaMiddleware from 'redux-saga';
import rootSaga from './utils/sagas';
import DevTools from './components/DevTools';

const sagaMiddleware = createSagaMiddleware();

let store = createStore(
  dawnApp,
  compose(
    applyMiddleware(sagaMiddleware),
    // For memory reasons, DevTools only keeps most recent {maxAge} actions
    DevTools.instrument({ maxAge: 30 })
  )
);

sagaMiddleware.run(rootSaga);

export { store, DevTools };
