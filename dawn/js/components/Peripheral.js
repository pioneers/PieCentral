/**
 * A component representing a particular peripheral.
 * A thin, discerning wrapper around the different periphal components.
 *
 * You should use this Peripheral class when handling any Peripheral whose subtype
 * you don't necessarily know.
 */

import React from 'react';
import {ListGroupItem} from 'react-bootstrap';
import {PeripheralTypes} from '../constants/Constants';
import GenericPeripheral from './peripherals/GenericPeripheral';
import Motor from './peripherals/Motor';
import BooleanSensor from './peripherals/BooleanSensor';
import ScalarSensor from './peripherals/ScalarSensor';
import ColorSensor from './peripherals/ColorSensor';

// Mapping between peripheral types and components
var typesToComponents = {};
typesToComponents[PeripheralTypes.MOTOR_SCALAR] = Motor;
typesToComponents[PeripheralTypes.SENSOR_BOOLEAN] = BooleanSensor;
typesToComponents[PeripheralTypes.SENSOR_SCALAR] = ScalarSensor;
typesToComponents[PeripheralTypes.LimitSwitch] = BooleanSensor;
typesToComponents[PeripheralTypes.LineFollower] = ScalarSensor;
typesToComponents[PeripheralTypes.Potentiometer] = ScalarSensor;
typesToComponents[PeripheralTypes.Encoder] = ScalarSensor;
typesToComponents[PeripheralTypes.ColorSensor] = ColorSensor;
typesToComponents[PeripheralTypes.MetalDetector] = ScalarSensor;


var Peripheral = React.createClass({
  propTypes: {
    peripheralType: React.PropTypes.string.isRequired
  },
  /**
   * Determines the specific type of peripheral that this object represents.
   */
  determinePeripheralComponent() {
    return typesToComponents[this.props.peripheralType];
  },
  /**
   * We render the specific peripheral corrensponding to the peripheralType.
   */
  render() {
    var SpecificPeripheralComponent = this.determinePeripheralComponent() || GenericPeripheral;
    return (
      <ListGroupItem>
        <SpecificPeripheralComponent {...this.props}/>
      </ListGroupItem>
    );
  }
});

export default Peripheral;
