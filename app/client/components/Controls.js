import React from 'react';
import {ButtonToolbar, Button} from 'react-bootstrap';
import AnsibleClient from '../utils/AnsibleClient';

var Controls = React.createClass({
  startRobot(){
    AnsibleClient.sendMessage('execute', {});
  },
  stopRobot(){
    AnsibleClient.sendMessage('stop', {});
  },
  render() {
    return (
      <ButtonToolbar>
        <Button bsStyle="success" onClick={ this.startRobot }>Start</Button>
        <Button bsStyle="danger" onClick={ this.stopRobot }>Stop</Button>
      </ButtonToolbar>
    );
  }
});

export default Controls;
