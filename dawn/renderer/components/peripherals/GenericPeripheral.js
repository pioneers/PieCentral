import React from 'react';
import _ from 'lodash';
import NameEditContainer from '../NameEditContainer';

/**
 * A generic peripheral, used when the peripheralType is unknown.
 */
const GenericPeripheral = props => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100%' }}>
      <h4 style={{ float: 'left' }}>
        <NameEditContainer name={props.device_name} id={props.id} />
        <small>{props.device_type}</small>
      </h4>
      {
        _.map(props.param, obj => (
          <h4 style={{ float: 'right' }} key={`${obj.param}-${props.device_name}`} >
            {`${obj.param}: ${obj[obj.kind]}`}
          </h4>
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
