import React from 'react';
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
            <NameEditContainer name={this.props.name} id={this.props.id} />
            <small> {this.props.peripheralType} </small>
          </h4>
          <h4
            style={{ float: 'right' }}
          >
            {BooleanSensor.formatBoolean(this.props.peripheralType, this.props.value)}
          </h4>
        </div>
      </div>
    );
  }
}

BooleanSensor.propTypes = {
  name: React.PropTypes.string.isRequired,
  peripheralType: React.PropTypes.string.isRequired,
  id: React.PropTypes.string.isRequired,
  value: React.PropTypes.number.isRequired,
};

export default BooleanSensor;
