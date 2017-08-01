import React from 'react';
import _ from 'lodash';
import { PeripheralTypes } from '../../constants/Constants';

/**
 * Boolean Sensor Component
 */
class BooleanSensor extends React.Component {
  static formatBoolean(peripheralType, sensorValue) {
    if (peripheralType === PeripheralTypes.LimitSwitch) {
      return (sensorValue) ? 'Closed' : 'Open';
    }
    return sensorValue; // TODO: Verify if int_value or bool_value
  }

  render() {
    return (
      <div style={{ overflow: 'auto' }}>
        <div style={{ overflow: 'auto', width: '100%' }}>
          <h4 style={{ float: 'left' }}>
            <div>{this.props.id}</div>
            <small> {this.props.device_type} </small>
          </h4>
          {
            _.map(this.props.param, obj => (
              <div key={`${obj.param}-${this.props.device_name}-Overall`}>
                <h4 style={{ float: 'right', height: '10px' }} key={`${obj.param}-${this.props.device_name}`}>
                  {`${obj.param}: ${BooleanSensor.formatBoolean(this.props.device_type, obj.int_value)}`}
                </h4>
                <div style={{ clear: 'both', height: '2px' }} key={`${obj.param}-${this.props.device_name}-Spacing`} />
              </div>
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
