import React from 'react';
import numeral from 'numeral';
import _ from 'lodash';

const ScalarSensor = props => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}>
        <div>{props.id}</div>
        <small>{props.device_type}</small>
      </h4>
      {
        _.map(props.param, obj => (
          <div key={`${obj.param}-${props.device_name}-Overall`}>
            <h4 style={{ float: 'right', height: '10px' }} key={`${obj.param}-${props.device_name}`}>
              {`${obj.param}: ${numeral(obj.float_value || obj.int_value).format('+0.00')}`}
            </h4>
            <div style={{ clear: 'both', height: '2px' }} key={`${obj.param}-${props.device_name}-Spacing`} />
          </div>
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
