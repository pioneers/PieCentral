import React from 'react';
import RobotActions from '../actions/RobotActions';
import {Button, Panel} from 'react-bootstrap';

var MotorTester = React.createClass({
  generateFakeData() {
    var id = '1337beef';
    var speed = Math.floor(Math.random() * 100);
    RobotActions.updateMotor(id, speed);
  },
  componentDidMount() {
    this.interval = setInterval(this.generateFakeData, 100);
  },
  componentWillUnmount() {
    clearInterval(this.interval);
  },
  render() {
    return <Panel header='Motor Tester' bsStyle='primary'>
      <Button bsStyle='success' onClick={this.generateFakeData}>Trigger Motor Update</Button>
    </Panel>;
  }
});

export default MotorTester;
