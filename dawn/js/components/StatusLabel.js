import React from 'react';
import {Label} from 'react-bootstrap';
import numeral from 'numeral';

var StatusLabel = React.createClass({
  propTypes: {
    connectionStatus: React.PropTypes.bool,
    runtimeStatus: React.PropTypes.bool,
    battery: React.PropTypes.number
  },
  render() {
    let labelStyle = 'default';
    let labelText = 'Disconnected';
    if (this.props.connectionStatus) {
      if (!this.props.runtimeStatus) {
        labelStyle = 'danger';
        labelText = 'Runtime Error';
      } else if (this.props.battery < 1) {
        labelStyle = 'warning';
        labelText = 'Battery Issue'
      } else {
        labelStyle = 'success';
        labelText = `Connected. Battery: ${numeral(this.props.battery).format('0.00')} V`;
      }
    }
    return (
      <Label bsStyle={labelStyle}>{labelText}</Label>
    );
  }
});

export default StatusLabel;
