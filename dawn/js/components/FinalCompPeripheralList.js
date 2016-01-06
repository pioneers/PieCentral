/**
 * Haxors
 */

import React from 'react';
import PeripheralList from './PeripheralList';
import Peripheral from './Peripheral';
import RobotPeripheralStore from '../stores/RobotPeripheralStore';
import _ from 'lodash';

var FinalCompPeripheralList = React.createClass({
  getInitialState() {
    return { peripherals: [] };
  },
  onChange() {
    this.setState({
      peripherals: RobotPeripheralStore.getPeripherals(),
    });
  },
  componentDidMount() {
    RobotPeripheralStore.on('change', this.onChange);
    this.onChange();
  },
  componentWillUnmount() {
    RobotPeripheralStore.removeListener('change', this.onChange);
  },
  render() {
    return (
      <PeripheralList header='Peripherals'>
        {this.props.connectionStatus
          ? _.map(this.state.peripherals, (peripheral) => <Peripheral key={peripheral.id} {...peripheral}/>)
          : 'You are currently disconnected from the robot.'}
      </PeripheralList>
    );
  }
});

export default FinalCompPeripheralList;
