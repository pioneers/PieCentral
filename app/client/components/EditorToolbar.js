import React from 'react';
import {Button, ButtonToolbar} from 'react-bootstrap';

var EditorToolbar = React.createClass({
  render() {
    return (
      <ButtonToolbar>
        <Button bsStyle='primary'>Save</Button>
      </ButtonToolbar>
    );
  }
});

export default EditorToolbar;
