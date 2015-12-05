/**
 * A component representing a motor.
 * Props:
 *   id: a unique id string
 *   value: the speed, from -100 to 100.
 *   disconnected: Boolean indicator if this motor is disconnected
 */

import React from 'react';
import {Label, ProgressBar} from 'react-bootstrap';
// https://react-bootstrap.github.io/components.html

var Motor = React.createClass({
  propTypes: {
    name: React.PropTypes.string,
    value: React.PropTypes.number
  },
  render() {
    return (
    <div style={{overflow: 'auto'}}>
      <div style={{overflow: 'auto', width: '100%'}}>
        <h4 style={{float: 'left'}}>{this.props.name}<small> Motor</small></h4>
        <h4 style={{float: 'right'}}>
        {
          this.props.disconnected
          ? <Label bsStyle='danger'>Disconnected</Label>
          : this.props.value
        }
        </h4>
      </div>
      <ProgressBar now={(this.props.value+100)/2} />
      // Center Bar at 0
    </div>
    );
  }
});

export default Motor;
