/* eslint-disable camelcase */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';
import numeral from 'numeral';

import { ProgressBar } from 'react-bootstrap';

/**
 *  Motor Component
 */
const Motor = ({ id, device_name, param }) => (
  <div style={{ overflow: 'auto', width: '100%' }}>
    <h4 style={{ float: 'left' }}>
      <div>{id}</div>
      <small>{'Motor'}</small>
    </h4>
    {
      _.map(param, obj => ( // TODO: Figure out if a ProgressBar is useful
        <div key={`${obj.param}-${device_name}-Overall`}>
          <h4 style={{ float: 'right', height: '10px' }} key={`${obj.param}-${device_name}`}>
            {`${obj.param}: ${numeral(obj.float_value).format('+0.00')}`}
            <ProgressBar now={obj.float_value} min={-100} />
          </h4>
        </div>
      ))
    }
  </div>
);

Motor.propTypes = {
  device_name: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  param: PropTypes.array.isRequired,
};

export default Motor;
