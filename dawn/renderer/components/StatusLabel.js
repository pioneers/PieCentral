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
    } else if (props.batterySafety) {
      labelStyle = 'danger';
      labelText = 'Unsafe Battery';
    } else {
      labelStyle = 'success';
      labelText = `Battery: ${numeral(props.battery).format('0.00')} V`;
    }
  }
  return (
    <Label bsStyle={labelStyle}>{labelText}</Label>
  );
};

StatusLabel.propTypes = {
  connectionStatus: React.PropTypes.bool.isRequired,
  runtimeStatus: React.PropTypes.bool.isRequired,
  battery: React.PropTypes.number.isRequired,
  batterySafety: React.PropTypes.bool.isRequired,
};

export default StatusLabel;
