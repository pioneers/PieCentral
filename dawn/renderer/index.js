import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
// import App from './components/App';
import store from './store';

const App = () => (
  <h1>It works</h1>
);

ReactDOM.render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('content'),
);
