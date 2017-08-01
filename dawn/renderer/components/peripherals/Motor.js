import React from 'react';
import _ from 'lodash';
import { ProgressBar } from 'react-bootstrap';
import numeral from 'numeral';

/**
 * A component representing a motor.
 */
const Motor = props => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}>
        <div>{props.id}</div>
        <small>{'Motor'}</small>
      </h4>
      {
        _.map(props.param, obj => (
          <div key={`${obj.param}-${props.device_name}-Overall`}>
            <h4 style={{ float: 'right', height: '10px' }} key={`${obj.param}-${props.device_name}`}>
              {`${obj.param}: ${numeral(obj.float_value).format('+0.00')}`}
              <ProgressBar now={obj.float_value} min={-100} />
            </h4>
            <div style={{ clear: 'both', height: '2px' }} key={`${obj.param}-${props.device_name}-Spacing`} />
          </div>
        ))
      }
    </div>
  </div>
);

Motor.propTypes = {
  device_name: React.PropTypes.string,
  id: React.PropTypes.string,
  param: React.PropTypes.array,
};

export default Motor;
