import React from 'react';
import numeral from 'numeral';
import _ from 'lodash';
import NameEditContainer from '../NameEditContainer';

const ScalarSensor = props => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}>
        <NameEditContainer name={props.device_name} id={props.id} />
        <small>{props.device_type}</small>
      </h4>
      {
        _.map(props.param, obj => (
          <h4 style={{ float: 'right' }} key={`${obj.param}-${props.device_name}`}>
            {`${obj.param}: ${numeral(obj[obj.kind]).format('+0.00')}`}
          </h4>
        ))
      }
    </div>
  </div>
);

ScalarSensor.propTypes = {
  device_name: React.PropTypes.string,
  device_type: React.PropTypes.string,
  id: React.PropTypes.string,
  param: React.PropTypes.array,
};

export default ScalarSensor;
