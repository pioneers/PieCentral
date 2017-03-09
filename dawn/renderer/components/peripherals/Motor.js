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
            <h4 style={{ float: 'right' }} key={`${obj.param}-${props.device_name}`}>
              {`${obj.param}: ${numeral(obj[obj.kind]).format('+0.00')}`}
              <ProgressBar now={obj[obj.kind]} min={-100} />
            </h4>
            <div style={{ clear: 'both' }} key={`${obj.param}-${props.device_name}-Spacing`} />
          </div>
        ))
      }
    </div>
  </div>
);

Motor.propTypes = {
  device_name: React.PropTypes.string,
  device_type: React.PropTypes.string,
  id: React.PropTypes.string,
  param: React.PropTypes.array,
};

export default Motor;
