import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import App from './components/App';
import { Provider } from 'react-redux';
import { store, DevTools } from './configureStore';

ReactDOM.render(
  <Provider store={store}>
    <div>
      <App/>
      <DevTools/>
    </div>
  </Provider>,
  document.getElementById('content')
);
