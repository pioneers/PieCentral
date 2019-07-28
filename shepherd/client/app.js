import React from 'react';
import ReactDOM from 'react-dom';
import { Provider, connect } from 'react-redux';
import { HashRouter, Redirect, Route, Switch } from 'react-router-dom';
import { Colors, FocusStyleManager } from '@blueprintjs/core';

import Dashboard from './dashboard';
import Scoreboard from './scoreboard';
import './messaging';
import store from './store';
import { LIGHT_THEME, DARK_THEME } from './util';
import './style.scss';

class App extends React.Component {
  render() {
    let className, background, theme = this.props.theme || LIGHT_THEME;
    if (theme === DARK_THEME) {
      className = 'bp3-dark';
      background = Colors.DARK_GRAY3;
    } else {
      className = 'bp3-light';
      background = Colors.LIGHT_GRAY5;
    }

    return (
      <HashRouter>
        <div className={`bg-theme bp3-text-large ${className}`} style={{ background }}>
          <Switch>
            <Route path='/dashboard' render={() => <Dashboard />} />
            <Route path='/scoreboard' render={() => <Scoreboard />} />
            <Redirect from='/' exact to='/dashboard' />
            <Route path='*' exact render={() => <p>Page Not Found</p>} />
          </Switch>
        </div>
      </HashRouter>
    );
  }
}

App = connect(state => ({ theme: state.theme }))(App);
FocusStyleManager.onlyShowFocusOnTabs();
ReactDOM.render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('app')
);
