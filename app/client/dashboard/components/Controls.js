import React from 'react';
import {Panel, ButtonToolbar, Button} from 'react-bootstrap';
import Environment from '../../utils/Environment';
if(Environment.isBrowser){
  var AnsibleClient = require('../../utils/AnsibleClient');
}

var Controls = React.createClass({
  startRobot(){
    AnsibleClient.sendMessage('execute', {});
  },
  stopRobot(){
    AnsibleClient.sendMessage('stop', {});
  },
  render() {
    if(Environment.isBrowser){
      return (
        <Panel header="Controls" bsStyle="primary">
          <ButtonToolbar>
            <Button bsStyle="primary" onClick={ this.startRobot }>Start</Button>
            <Button bsStyle="danger" onClick={ this.stopRobot }>Stop</Button>
          </ButtonToolbar>
        </Panel>
      );
    } else {
      return (<p>Loading</p>);
    }
  }
});

export default Controls;
