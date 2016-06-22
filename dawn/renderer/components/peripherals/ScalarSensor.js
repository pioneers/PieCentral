import React from 'react';
import NameEdit from '../NameEdit';
import numeral from 'numeral';

const ScalarSensor = (props) => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}>
        <NameEdit name={props.name} id={props.id} />
        <small> {props.peripheralType} </small>
      </h4>
      <h4 style={{ float: 'right' }}> {numeral(props.value).format('0.00')} </h4>
    </div>
  </div>
);

ScalarSensor.propTypes = {
  name: React.PropTypes.string,
  peripheralType: React.PropTypes.string,
  id: React.PropTypes.string,
  value: React.PropTypes.number,
};

export default ScalarSensor;
