import React from 'react';
import {Route, IndexRoute} from 'react-router';
import App from './components/App';
import Dashboard from './components/Dashboard';

var Routes = (
  <Route path="/" component={App}>
    <IndexRoute component={Dashboard} />
  </Route>
);

export default Routes;
