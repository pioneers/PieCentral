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
    let errorMsg = null;
    if (!this.props.connectionStatus) {
      errorMsg = 'You are currently disconnected from the robot.';
    } else if (!this.props.runtimeStatus) {
      errorMsg = 'There appears to be some sort of Runtime error. No data is being received.';
    }
    return (
      <PeripheralList header='Peripherals'>
        {!errorMsg
          ? _.map(this.state.peripherals, (peripheral) => <Peripheral key={peripheral.id} {...peripheral}/>)
          : errorMsg}
      </PeripheralList>
    );
  }
});

export default FinalCompPeripheralList;
