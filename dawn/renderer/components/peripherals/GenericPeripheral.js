import React from 'react';
import NameEditContainer from '../NameEditContainer';

/**
 * A generic peripheral, used when the peripheralType is unknown.
 */
const GenericPeripheral = (props) => (
  <div style={{ overflow: 'auto' }}>
    <div style={{ overflow: 'auto', width: '100' }}>
      <h4 style={{ float: 'left' }}>
        <NameEditContainer name={props.name} id={props.id} />
        <small>{props.peripheralType}</small>
      </h4>
      <h4 style={{ float: 'right' }}>
        {props.value}
      </h4>
    </div>
  </div>
);

GenericPeripheral.propTypes = {
  name: React.PropTypes.string,
  id: React.PropTypes.string,
  peripheralType: React.PropTypes.string,
  value: React.PropTypes.oneOfType([
    React.PropTypes.string,
    React.PropTypes.number,
  ]),
};

GenericPeripheral.defaultProps = {
  peripheralType: 'peripheralType was undefined',
};

export default GenericPeripheral;
