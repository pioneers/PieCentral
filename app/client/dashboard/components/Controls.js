import React from 'react';
import {Panel, ButtonToolbar, Button} from 'react-bootstrap';
import AnsibleClient from '../../utils/AnsibleClient';

var Controls = React.createClass({
  startRobot(){
    AnsibleClient.sendMessage('execute', {});
  },
  stopRobot(){
    AnsibleClient.sendMessage('stop', {});
  },
  render() {
    return (
      <Panel header="Controls" bsStyle="primary">
        <ButtonToolbar>
          <Button bsStyle="primary" onClick={ this.startRobot }>Start</Button>
          <Button bsStyle="danger" onClick={ this.stopRobot }>Stop</Button>
        </ButtonToolbar>
      </Panel>
    );
  }
});

export default Controls;
