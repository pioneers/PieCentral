import React from 'react';
import ReactDOM from 'react-dom';
import './style.scss';

import { Spinner, Intent } from '@blueprintjs/core';

class App extends React.Component {
  render() {
    return (
      <Spinner intent={Intent.PRIMARY} />
    )
  }
}

ReactDOM.render(<App />, document.getElementById('app'));
