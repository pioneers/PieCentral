/**
 * A component representing a boolean sensor.
 * Props:
 *   id: a unique id string
 *   value: Boolean, whether the sensor is sending a high value
 */

import React from 'react';

var BooleanSensor = React.createClass({
  propTypes: {
    id: React.PropTypes.string,
    speed: React.PropTypes.number
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}>Boolean Sensor <small>{this.props.id}</small></h4>
        <h4 style={{float: 'right'}}> {this.props.value} </h4>
      </div>
    </div>
    );
  }
});

export default BooleanSensor;
