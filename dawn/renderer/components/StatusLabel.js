import React from 'react';
import { Label } from 'react-bootstrap';
import numeral from 'numeral';

const StatusLabel = (props) => {
  let labelStyle = 'default';
  let labelText = 'Disconnected';
  if (props.connectionStatus) {
    if (!props.runtimeStatus) {
      labelStyle = 'danger';
      labelText = 'Runtime Error';
    } else if (props.battery < 1) {
      labelStyle = 'warning';
      labelText = 'Battery Issue';
    } else {
      labelStyle = 'success';
      labelText = `Connected. Battery: ${numeral(props.battery).format('0.00')} V`;
    }
  }
  return (
    <Label bsStyle={labelStyle}>{labelText}</Label>
  );
};

StatusLabel.propTypes = {
  connectionStatus: React.PropTypes.bool,
  runtimeStatus: React.PropTypes.bool,
  battery: React.PropTypes.number,
};

export default StatusLabel;
