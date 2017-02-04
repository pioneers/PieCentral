import React from 'react';
import { ProgressBar } from 'react-bootstrap';
import numeral from 'numeral';
import NameEditContainer from '../NameEditContainer';

/**
 * A component representing a motor.
 */
const Motor = props => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}><NameEditContainer name={props.name} id={props.id} />
        <small> Motor</small>
      </h4>
      <h4 style={{ float: 'right' }}>
        {numeral(props.value).format('+0.00')}
      </h4>
    </div>
    <ProgressBar now={props.value} min={-100} />
  </div>
);

Motor.propTypes = {
  name: React.PropTypes.string.isRequired,
  value: React.PropTypes.number.isRequired,
  id: React.PropTypes.string.isRequired,
};

export default Motor;
