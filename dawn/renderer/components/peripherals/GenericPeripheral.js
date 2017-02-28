import React from 'react';
import _ from 'lodash';
import NameEditContainer from '../NameEditContainer';

/**
 * A generic peripheral, used when the peripheralType is unknown.
 */
class GenericPeripheral extends React.Component {
  render() {
    return (
      <div style={{ overflow: 'auto' }}>
        <div style={{ overflow: 'auto', width: '100%' }}>
          <h4 style={{ float: 'left' }}>
            <NameEditContainer name={this.props.device_name} id={this.props.id} />
            <small>{this.props.device_type}</small>
          </h4>
          {
            _.map(this.props.param, obj => (
              <h4 style={{ float: 'right' }} key={`${obj.param}-${this.props.device_name}`} >
                {`${obj.param}: ${obj[obj.kind]}`}
              </h4>
            ))
          }
        </div>
      </div>
    );
  }
}

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
