import React from 'react';
import NameEditContainer from '../NameEditContainer';
import numeral from 'numeral';
import { ProgressBar } from 'react-bootstrap';

/**
 * A component representing a motor.
 */
const Motor = (props) => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}><NameEditContainer name={props.name} id={props.id} />
        <small> Motor</small>
      </h4>
      <h4 style={{ float: 'right' }}>
        {numeral(props.value).format('+0.00')}
      </h4>
    </div>
    <ProgressBar now={Math.abs(props.value)} />
  </div>
);

Motor.propTypes = {
  name: React.PropTypes.string,
  value: React.PropTypes.number,
  id: React.PropTypes.string,
};

export default Motor;
