import React from 'react';
import ReactDOM from 'react-dom';
import {Router, Route, IndexRoute} from 'react-router';
import App from './components/App';
import Dashboard from './components/Dashboard';
import Routes from './routes';

ReactDOM.render((
  <Router>
    {Routes}
  </Router>
), document.getElementById('react-app'));
