/**
 * A self-contained component that displays all the currently
 * connected motors from RemoteRobotStore.
 */

import React from 'react';
import RemoteRobotStore from '../stores/RemoteRobotStore';
import Peripheral from './Peripheral';
import PeripheralList from './PeripheralList';
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
    return <PeripheralList header='Motors'>
      {_.map(this.state.motors, (motor) => <Peripheral key={motor.id} {...motor}/>)}
    </PeripheralList>;
  }
});

export default MotorList;
