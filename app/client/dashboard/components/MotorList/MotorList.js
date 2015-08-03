import React from 'react';
import RemoteRobotStore from '../../stores/RemoteRobotStore';
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
  componentWillUnmount() {
    RemoteRobotStore.removeListener('change', this.onChange);
  },
  render() {
    return <Panel header='Motors' bsStyle='primary'>
      {_.map(this.state.motors, (motor) => <Motor key={motor.id} {...motor}/>)}
    </Panel>;
  }
});

export default MotorList;
