/**
 * Haxors
 */

import React from 'react';
import _ from 'lodash';
import PeripheralList from './PeripheralList';
import Peripheral from './Peripheral';

const FinalCompPeripheralList = (props) => {
  let errorMsg = null;
  if (!props.connectionStatus) {
    errorMsg = 'You are currently disconnected from the robot.';
  } else if (!props.runtimeStatus) {
    errorMsg = 'There appears to be some sort of Runtime error. ' +
      'No data is being received.';
  }
  return (
    <PeripheralList header="Peripherals">
      {
        !errorMsg ?
        _.map(
          _.toArray(props.peripherals), peripheral => (
            <Peripheral
              key={String(peripheral.uid.high) + String(peripheral.uid.low)}
              id={String(peripheral.uid.high) + String(peripheral.uid.low)}
              name={peripheral.device_name}
              value={peripheral.value}
              peripheralType={peripheral.device_type}
            />
          ),
        ) : <p className="panelText">{errorMsg}</p>
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
