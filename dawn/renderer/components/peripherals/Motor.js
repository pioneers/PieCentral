import React from 'react';
import _ from 'lodash';
import { ProgressBar } from 'react-bootstrap';
import numeral from 'numeral';
import NameEditContainer from '../NameEditContainer';

/**
 * A component representing a motor.
 */
const Motor = (props) => {
  return (
    <div style={{ overflow: 'auto' }}>
      <div style={{ overflow: 'auto', width: '100%' }}>
        <h4 style={{ float: 'left' }}>
          <NameEditContainer name={props.device_name} id={props.id} />
          <small>{'Motor'}</small>
        </h4>
        {
          _.map(props.param, obj => (
            <h4 style={{ float: 'right' }} key={`${obj.param}-${props.device_name}`}>
              {`${obj.param}: ${numeral(obj[obj.kind]).format('+0.00')}`}
              <ProgressBar now={obj[obj.kind]} min={-100} />
            </h4>
          ))
        }
      </div>
    </div>
  );
};

Motor.propTypes = {
  device_name: React.PropTypes.string,
  device_type: React.PropTypes.string,
  id: React.PropTypes.string,
  param: React.PropTypes.array,
};

export default Motor;
