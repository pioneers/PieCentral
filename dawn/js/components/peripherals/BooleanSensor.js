/**
 * A component representing a boolean sensor.
 * Props:
 *   id: a unique id string
 *   value: Boolean, whether the sensor is sending a high value
 */

import React from 'react';
import NameEdit from './NameEdit';

var _booleanDisplay = function(sensor) {
  if (sensor.peripheralType == "LimitSwitch") {
    return (sensor.value) ? "Closed":"Open";
  } else return sensor.value;
};

var BooleanSensor = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    peripheralType: React.PropTypes.string,
    id: React.PropTypes.string,
    value: React.PropTypes.number
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}><NameEdit name={this.props.name} id={this.props.id} /><small> {this.props.peripheralType} </small></h4>
        <h4 style={{float: 'right'}}> {_booleanDisplay(this.props)} </h4>
      </div>
    </div>
    );
  }
});

export default BooleanSensor;
