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
import Motor from './peripherals/Motor';
import BooleanSensor from './peripherals/BooleanSensor';

// Mapping between peripheral types and components
const defaultPeripheral = {
  get: (target, name) => (
    Object.prototype.hasOwnProperty.call(target, name) ? target[name] : GenericPeripheral
  ),
};

const typesToComponents = new Proxy({}, defaultPeripheral);
typesToComponents[PeripheralTypes.MOTOR_SCALAR] = Motor;
typesToComponents[PeripheralTypes.SENSOR_BOOLEAN] = BooleanSensor;
typesToComponents[PeripheralTypes.LimitSwitch] = BooleanSensor;

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
