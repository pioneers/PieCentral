/**
 * Haxors
 */

import React from 'react';
import PeripheralList from './PeripheralList';
import Peripheral from './Peripheral';
import _ from 'lodash';

const FinalCompPeripheralList = (props) => {
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
            key={String(peripheral.uid.high) + String(peripheral.uid.low)}
            id={String(peripheral.uid.high) + String(peripheral.uid.low)}
            name={peripheral.device_name}
            value={peripheral.value}
            peripheralType={peripheral.device_type}
          />
        )
      ) : errorMsg
    }
    </PeripheralList>
  );
};

FinalCompPeripheralList.propTypes = {
  connectionStatus: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  peripherals: React.PropTypes.object,
};

export default FinalCompPeripheralList;
