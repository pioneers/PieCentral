import React from 'react';
import RobotActions from '../actions/RobotActions';
import {Button, ButtonGroup, Panel} from 'react-bootstrap';

var MotorTester = React.createClass({
  getInitialState() {
    return {
      id: '1337beef'
    };
  },
  generateFakeData() {
    var speed = Math.floor(Math.random() * 100);
    RobotActions.updateMotor(this.state.id, speed);
  },
  componentDidMount() {
    this.interval = setInterval(this.generateFakeData, 100);
  },
  componentWillUnmount() {
    clearInterval(this.interval);
  },
  changeMotorName() {
    this.setState({id: String(Math.floor(Math.random() * 100))});
  },
  render() {
    return <Panel header='Motor Tester' bsStyle='primary'>
      <ButtonGroup>
        <Button bsStyle='success' onClick={this.generateFakeData}>Trigger Motor Update</Button>
        <Button bsStyle='success' onClick={this.changeMotorName}>Change Motor Name</Button>
      </ButtonGroup>
    </Panel>;
  }
});

export default MotorTester;
