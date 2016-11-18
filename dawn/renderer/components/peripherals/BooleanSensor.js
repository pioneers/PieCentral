import React from 'react';
import NameEditContainer from '../NameEditContainer';
import { PeripheralTypes } from '../../constants/Constants';

/**
 * A component representing a boolean sensor,
 * for example a LimitSwitch.
 */
class BooleanSensor extends React.Component {
  constructor(props) {
    super(props);
    this.formatBoolean = this.formatBoolean.bind(this);
  }

  /**
   * Formats data for display based on peripheralType.
   */
  formatBoolean(peripheralType, sensorValue) {
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
            {this.formatBoolean(this.props.peripheralType, this.props.value)}
          </h4>
        </div>
      </div>
    );
  }
}

BooleanSensor.propTypes = {
  name: React.PropTypes.string,
  peripheralType: React.PropTypes.string,
  id: React.PropTypes.string,
  value: React.PropTypes.number,
};

export default BooleanSensor;
