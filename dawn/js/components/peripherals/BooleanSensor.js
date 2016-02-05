/**
 * A component representing a boolean sensor.
 * Props:
 *   id: a unique id string
 *   value: Boolean, whether the sensor is sending a high value
 */

import React from 'react';
import NameEdit from './NameEdit';

var BooleanSensor = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    speed: React.PropTypes.number
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}><NameEdit name={this.props.name} id={this.props.id} /><small> Boolean Sensor</small></h4>
        <h4 style={{float: 'right'}}> {this.props.value} </h4>
      </div>
    </div>
    );
  }
});

export default BooleanSensor;
