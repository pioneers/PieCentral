import React from 'react';
import {Panel} from 'react-bootstrap';

var Motor = React.createClass({
  propTypes: {
    motor: React.PropTypes.object
  },
  render() {
    return <Panel header='Motor'>
      id: {this.props.motor.id}, speed: {this.props.motor.speed}
    </Panel>;
  }
});

export default Motor;
