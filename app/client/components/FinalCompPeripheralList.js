/**
 * Haxors
 */

import React from 'react';
import PeripheralList from './PeripheralList';
import Peripheral from './Peripheral';
import RemoteRobotStore from '../stores/RemoteRobotStore';
import _ from 'lodash';

var FinalCompPeripheralList = React.createClass({
  getInitialState() {
    return {
      peripherals: [],
      connection: true
    };
  },
  onChange() {
    this.setState({
      peripherals: RemoteRobotStore.getPeripherals(),
      connection: RemoteRobotStore.getConnectionStatus()
    });
  },
  componentDidMount() {
    RemoteRobotStore.on('change', this.onChange);
    this.onChange();
  },
  componentWillUnmount() {
    RemoteRobotStore.removeListener('change', this.onChange);
  },
  render() {
    return (
      <PeripheralList header='Peripherals'>
        {this.state.connection
          ? _.map(this.state.peripherals, (peripheral) => <Peripheral key={peripheral.id} {...peripheral}/>)
          : 'You are currently disconnected from the robot.'}
      </PeripheralList>
    );
  }
});

export default FinalCompPeripheralList;
