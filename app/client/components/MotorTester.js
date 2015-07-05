import React from 'react';
import RobotActions from '../actions/RobotActions';
import {Button, Panel} from 'react-bootstrap';

var MotorTester = React.createClass({
  onClick() {
    var id = 'test id';
    var speed = Math.random();
    RobotActions.updateMotor(id, speed);
  },
  render() {
    return <Panel header='Motor Tester'>
      <Button onClick={this.onClick}>Click Me</Button>
    </Panel>;
  }
});

export default MotorTester;
