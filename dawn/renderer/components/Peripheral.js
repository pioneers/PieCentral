/**
 * A component representing a particular peripheral.
 * A thin, discerning wrapper around the different periphal components.
 *
 * You should use this Peripheral class when handling any Peripheral whose subtype
 * you don't necessarily know.
 */

import React from 'react';
import { ListGroupItem } from 'react-bootstrap';
import { PeripheralTypes } from '../constants/Constants';
import GenericPeripheral from './peripherals/GenericPeripheral';
import ScalarSensor from './peripherals/ScalarSensor';
import Motor from './peripherals/Motor';
import BooleanSensor from './peripherals/BooleanSensor';

// Mapping between peripheral types and components
const typesToComponents = {};
typesToComponents[PeripheralTypes.MOTOR_SCALAR] = Motor;
typesToComponents[PeripheralTypes.SENSOR_BOOLEAN] = BooleanSensor;
typesToComponents[PeripheralTypes.SENSOR_SCALAR] = ScalarSensor;
typesToComponents[PeripheralTypes.LimitSwitch] = BooleanSensor;
typesToComponents[PeripheralTypes.LineFollower] = ScalarSensor;
typesToComponents[PeripheralTypes.Potentiometer] = ScalarSensor;
typesToComponents[PeripheralTypes.Encoder] = ScalarSensor;
// typesToComponents[PeripheralTypes.ColorSensor] = ScalarSensor;
typesToComponents[PeripheralTypes.MetalDetector] = ScalarSensor;
typesToComponents[PeripheralTypes.ServoControl] = ScalarSensor;
typesToComponents[PeripheralTypes.YogiBear] = ScalarSensor;
typesToComponents[PeripheralTypes.RFID] = ScalarSensor;

class Peripheral extends React.Component {
  /**
   * Determines the specific type of peripheral that this object represents.
   */
  determinePeripheralComponent() {
    return typesToComponents[this.props.device_type];
  }

  /**
   * We render the specific peripheral corresponding to the peripheralType.
   */
  render() {
    const SpecificPeripheralComponent = this.determinePeripheralComponent() || GenericPeripheral;
    return (
      <ListGroupItem style={{ padding: '0px' }}>
        <SpecificPeripheralComponent {...this.props} />
      </ListGroupItem>
    );
  }
}

Peripheral.propTypes = {
  device_type: React.PropTypes.string,
};

export default Peripheral;
