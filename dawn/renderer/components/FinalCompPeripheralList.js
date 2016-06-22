/**
 * Haxors
 */

import React from 'react';
import PeripheralList from './PeripheralList';
import Peripheral from './Peripheral';
import { connect } from 'react-redux';
import _ from 'lodash';

const FinalCompPeripheralListComponent = (props) => {
  let errorMsg = null;
  if (!props.connectionStatus) {
    errorMsg = 'You are currently disconnected from the robot.';
  } else if (!props.runtimeStatus) {
    errorMsg = 'There appears to be some sort of Runtime error. No data is being received.';
  }
  return (
    <PeripheralList header="Peripherals">
    {
      !errorMsg ?
      _.map(
        _.toArray(props.peripherals),
        (peripheral) => (
          <Peripheral
            key={peripheral.id}
            id={peripheral.id}
            name={peripheral.name}
            value={peripheral.value}
            peripheralType={peripheral.peripheralType}
          />
        )
      ) : errorMsg
    }
    </PeripheralList>
  );
};

FinalCompPeripheralListComponent.propTypes = {
  connectionStatus: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  peripherals: React.PropTypes.object,
};

const mapStateToProps = (state) => ({
  peripherals: state.peripherals,
});

const FinalCompPeripheralList = connect(mapStateToProps)(FinalCompPeripheralListComponent);

export default FinalCompPeripheralList;
