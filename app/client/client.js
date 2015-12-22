import React from 'react';
import ReactDOM from 'react-dom';
import {Router, Route, IndexRoute} from 'react-router';
import App from './components/App';
import Dashboard from './components/Dashboard';

ReactDOM.render((
  <Router>
    <Route path="/" component={App}>
      <IndexRoute component={Dashboard} />
    </Route>
  </Router>
), document.getElementById('react-app'));
