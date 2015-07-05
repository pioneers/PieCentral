import React from 'react';
import RemoteRobotStore from '../stores/RemoteRobotStore';
import Motor from './Motor';
import {Panel} from 'react-bootstrap';
import _ from 'lodash';

var MotorList = React.createClass({
  getInitialState() {
    return {
      motors: {}
    };
  },
  onChange() {
    this.setState({motors: RemoteRobotStore.getMotors()});
  },
  componentDidMount() {
    RemoteRobotStore.on('change', this.onChange);
    this.onChange(); // call it once to refresh
  },
  render() {
    return <Panel header='Motor List'>
      This is a list of motors.
      {_.map(this.state.motors, (motor) => <Motor key={motor.id} motor={motor}/>)}
    </Panel>;
  }
});

export default MotorList;
