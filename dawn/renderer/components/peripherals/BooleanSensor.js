/* eslint-disable camelcase */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';
import { PeripheralTypes } from '../../constants/Constants';

/**
 * Boolean Sensor Component
 */
const formatBoolean = (peripheralType, sensorValue) => {
  if (peripheralType === PeripheralTypes.LimitSwitch) {
    return (sensorValue) ? 'Closed' : 'Open';
  }
  return sensorValue; // TODO: Verify if int_value or bool_value
};

const BooleanSensor = ({ id, device_name, device_type, param }) => (
  <div style={{ overflow: 'auto', width: '100%' }}>
    <h4 style={{ float: 'left' }}>
      <div>{id}</div>
      <small> {device_type} </small>
    </h4>
    {
      _.map(param, obj => (
        <div key={`${obj.param}-${device_name}-Overall`}>
          <h4 style={{ float: 'right', height: '10px' }} key={`${obj.param}-${device_name}`}>
            {`${obj.param}: ${formatBoolean(device_type, obj.int_value)}`}
          </h4>
        </div>
      ))
    }
  </div>
);

BooleanSensor.propTypes = {
  device_name: PropTypes.string.isRequired,
  device_type: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  param: PropTypes.array.isRequired,
};

export default BooleanSensor;
