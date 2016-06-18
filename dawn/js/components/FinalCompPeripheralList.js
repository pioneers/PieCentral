/**
 * Haxors
 */

import React from 'react';
import PeripheralList from './PeripheralList';
import Peripheral from './Peripheral';
import { connect } from 'react-redux';
import _ from 'lodash';

var FinalCompPeripheralList = React.createClass({
  render() {
    let errorMsg = null;
    if (!this.props.connectionStatus) {
      errorMsg = 'You are currently disconnected from the robot.';
    } else if (!this.props.runtimeStatus) {
      errorMsg = 'There appears to be some sort of Runtime error. No data is being received.';
    }
    return (
      <PeripheralList header='Peripherals'>
      {
        !errorMsg ?
        _.map(
          _.toArray(this.props.peripherals),
          (peripheral) => {
            return (
              <Peripheral
                key={peripheral.id}
                id={peripheral.id}
                name={peripheral.name}
                value={peripheral.value}
                peripheralType={peripheral.peripheralType}/>
            );
          }
        ) : errorMsg
      }
      </PeripheralList>
    );
  }
});

const mapStateToProps = (state) => {
  return {
    peripherals: state.peripherals
  };
};

FinalCompPeripheralList = connect(mapStateToProps)(FinalCompPeripheralList);

export default FinalCompPeripheralList;
