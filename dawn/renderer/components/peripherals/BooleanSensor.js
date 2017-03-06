import React from 'react';
import _ from 'lodash';
import NameEditContainer from '../NameEditContainer';
import { PeripheralTypes } from '../../constants/Constants';

/**
 * A component representing a boolean sensor,
 * for example a LimitSwitch.
 */
class BooleanSensor extends React.Component {
  /**
   * Formats data for display based on peripheralType.
   */
  static formatBoolean(peripheralType, sensorValue) {
    if (peripheralType === PeripheralTypes.LimitSwitch) {
      return (sensorValue) ? 'Open' : 'Closed';
    }
    return sensorValue;
  }

  render() {
    return (
      <div style={{ overflow: 'auto' }}>
        <div style={{ overflow: 'auto', width: '100%' }}>
          <h4 style={{ float: 'left' }}>
            <NameEditContainer name={this.props.device_name} id={this.props.id} />
            <small> {this.props.device_type} </small>
          </h4>
          {
            _.map(this.props.param, obj => (
              <h4 style={{ float: 'right' }} key={`${obj.param}-${this.props.device_name}`}>
                {`${obj.param}: ${BooleanSensor.formatBoolean(this.props.device_type, obj[obj.kind])}`}
              </h4>
            ))
          }
        </div>
      </div>
    );
  }
}

BooleanSensor.propTypes = {
  device_name: React.PropTypes.string,
  device_type: React.PropTypes.string,
  id: React.PropTypes.string,
  param: React.PropTypes.array,
};

export default BooleanSensor;
