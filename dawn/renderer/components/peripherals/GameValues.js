/* eslint-disable camelcase */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

/**
 * Generic Peripheral for General Case
 */
const GameValues = ({
  device_name, param,
}) => (
  <div style={{ overflow: 'auto', width: '100%' }}>
    <h4 style={{ float: 'left' }}>
      <div>{device_name}</div>
    </h4>
    {
      _.map(param, obj => (
        <div key={`${obj.param}-${device_name}-Overall`}>
          <h4 style={{ clear: 'right', float: 'right', height: '10px' }} key={`${obj.param}-${device_name}`} >
            {obj.int_value}
          </h4>
        </div>
      ))
    }
  </div>
);

GameValues.propTypes = {
  device_name: PropTypes.string,
  param: PropTypes.array.isRequired,
};

GameValues.defaultProps = {
  device_name: 'Unknown Device',
};

export default GameValues;
