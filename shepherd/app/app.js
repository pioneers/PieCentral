import React from 'react';
import ReactDOM from 'react-dom';

class App extends React.Component {
  render() {
    return (
      <pre>Working render</pre>
    )
  }
}

ReactDOM.render(<App />, document.getElementById('app'));
