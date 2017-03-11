import React from 'react';
import _ from 'lodash';
import numeral from 'numeral';

/**
 * A generic peripheral, used when the peripheralType is unknown.
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
              {`${obj.param}: ${numeral(obj[obj.kind]).format('+0.00')}`}
            </h4>
            <div style={{ clear: 'both', height: '2px' }} key={`${obj.param}-${props.device_name}-Spacing`} />
          </div>
        ))
      }
    </div>
  </div>
);

GenericPeripheral.propTypes = {
  device_name: React.PropTypes.string,
  device_type: React.PropTypes.string,
  id: React.PropTypes.string,
  param: React.PropTypes.array,
};

GenericPeripheral.defaultProps = {
  device_type: 'Undefined Type',
};

export default GenericPeripheral;
