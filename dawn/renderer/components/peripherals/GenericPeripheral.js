/* eslint-disable camelcase */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';
import numeral from 'numeral';

/**
 * Generic Peripheral for General Case
 */
const GenericPeripheral = ({
  id, device_name, param,
}) => (
  <div style={{ overflow: 'auto', width: '100%' }}>
    <h4 style={{ float: 'left' }}>
      <div>{id}</div>
    </h4>
    {
      _.map(param, (obj) => (
        <div key={`${obj.param}-${device_name}-Overall`}>
          <h4 style={{ clear: 'right', float: 'right', height: '10px' }} key={`${obj.param}-${device_name}`}>
            {`${obj.param}: ${numeral(obj.int_value || obj.float_value).format('+0.00')}`}
          </h4>
        </div>
      ))
    }
  </div>
);

GenericPeripheral.propTypes = {
  device_name: PropTypes.string,
  id: PropTypes.string.isRequired,
  param: PropTypes.array.isRequired,
};

GenericPeripheral.defaultProps = {
  device_name: 'Unknown Device',
};

export default GenericPeripheral;
