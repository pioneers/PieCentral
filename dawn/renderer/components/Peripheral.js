/**
 * Outer Component for Individual Peripherals
 *
 * Sets common interface for type-specific components
 * Wraps such components in ListGroupItem for PeripheralList.js
 */

import React from 'react';
import PropTypes from 'prop-types';
import { ListGroupItem } from 'react-bootstrap';
import { PeripheralTypes } from '../constants/Constants';
import BooleanSensor from './peripherals/BooleanSensor';
import GenericPeripheral from './peripherals/GenericPeripheral';
import GameValues from './peripherals/GameValues';
import Motor from './peripherals/Motor';

// Mapping between peripheral types and components
const typesToComponents = {};
typesToComponents[PeripheralTypes.MOTOR_SCALAR] = Motor;
typesToComponents[PeripheralTypes.SENSOR_BOOLEAN] = BooleanSensor;
typesToComponents[PeripheralTypes.LimitSwitch] = BooleanSensor;
typesToComponents[PeripheralTypes.GameValues] = GameValues;


const Peripheral = (props) => {
  const ActualPeripheral = typesToComponents[props.device_type] || GenericPeripheral;
  return (
    <ListGroupItem style={{ padding: '0px 0px 15px 0px', border: 'none' }}>
      <ActualPeripheral
        id={props.id}
        device_type={props.device_type}
        device_name={props.device_name}
        param={props.param}
      />
    </ListGroupItem>
  );
};

Peripheral.propTypes = {
  id: PropTypes.string,
  device_type: PropTypes.string.isRequired,
  device_name: PropTypes.string,
  param: PropTypes.any,
};

export default Peripheral;
