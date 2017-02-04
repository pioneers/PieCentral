import React from 'react';
import numeral from 'numeral';

import NameEditContainer from '../NameEditContainer';

const ScalarSensor = props => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}>
        <NameEditContainer name={props.name} id={props.id} />
        <small> {props.peripheralType} </small>
      </h4>
      <h4 style={{ float: 'right' }}> {numeral(props.value).format('0.00')} </h4>
    </div>
  </div>
);

ScalarSensor.propTypes = {
  name: React.PropTypes.string.isRequired,
  peripheralType: React.PropTypes.string.isRequired,
  id: React.PropTypes.string.isRequired,
  value: React.PropTypes.number.isRequired,
};

export default ScalarSensor;
