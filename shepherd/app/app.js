import React from 'react';
import ReactDOM from 'react-dom';
import Dashboard from './dashboard';
import './style.scss';
import { Colors, FocusStyleManager } from '@blueprintjs/core';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { theme: 'dark' };
  }

  render() {
    let className, background;
    if (this.state.theme === 'dark') {
      className = 'bp3-dark';
      background = Colors.DARK_GRAY3;
    } else {
      className = 'bp3-light';
      background = Colors.LIGHT_GRAY5;
    }
    return (
      <div className={`bg-theme ${className}`} style={{ background }}>
        <div className='container'>
          <Dashboard />
        </div>
      </div>
    );
  }
}

FocusStyleManager.onlyShowFocusOnTabs();
ReactDOM.render(<App />, document.getElementById('app'));
