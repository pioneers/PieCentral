import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';
import numeral from 'numeral';

/**
 * Generic Peripheral for General Case
 */
const GenericPeripheral = props => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}>
        <div>{props.id}</div>
        <small>{props.device_type}</small>
      </h4>
      {
        _.map(props.param, obj => (
          <div key={`${obj.param}-${props.device_name}-Overall`}>
            <h4 style={{ float: 'right', height: '10px' }} key={`${obj.param}-${props.device_name}`} >
              {`${obj.param}: ${numeral(obj.int_value || obj.float_value).format('+0.00')}`}
            </h4>
            <div style={{ clear: 'both', height: '2px' }} key={`${obj.param}-${props.device_name}-Spacing`} />
          </div>
        ))
      }
    </div>
  </div>
);

GenericPeripheral.propTypes = {
  device_name: PropTypes.string,
  device_type: PropTypes.string,
  id: PropTypes.string,
  param: PropTypes.array,
};

GenericPeripheral.defaultProps = {
  device_type: 'Undefined Type',
};

export default GenericPeripheral;
