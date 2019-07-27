import React from 'react';
import { HashRouter, Redirect, Route, Switch } from 'react-router-dom';
import ReactDOM from 'react-dom';
import { Colors, FocusStyleManager } from '@blueprintjs/core';

import Dashboard from './dashboard';
import Scoreboard from './scoreboard';
import { LIGHT_THEME, DARK_THEME } from './util';
import './style.scss';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { theme: DARK_THEME };
  }

  render() {
    let className, background, theme = this.state.theme || LIGHT_THEME;
    if (theme === DARK_THEME) {
      className = 'bp3-dark';
      background = Colors.DARK_GRAY3;
    } else {
      className = 'bp3-light';
      background = Colors.LIGHT_GRAY5;
    }

    let themeProps = {
      theme,
      toggleTheme: () => this.setState({
        theme: this.state.theme === DARK_THEME ? LIGHT_THEME : DARK_THEME
      })
    };

    return (
      <HashRouter>
        <div className={`bg-theme bp3-text-large ${className}`} style={{ background }}>
          <div className='container'>
            <Switch>
              <Route path='/dashboard' render={() => <Dashboard {...themeProps} />} />
              <Route path='/scoreboard' render={() => <Scoreboard {...themeProps} />} />
              <Redirect from='/' exact to='/dashboard' />
              <Route path='*' exact render={() => <p>Page Not Found</p>} />
            </Switch>
          </div>
        </div>
      </HashRouter>
    );
  }
}

FocusStyleManager.onlyShowFocusOnTabs();
ReactDOM.render(<App />, document.getElementById('app'));
