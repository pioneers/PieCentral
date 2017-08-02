import React from 'react';
import PropTypes from 'prop-types';
import { Label } from 'react-bootstrap';
import { connect } from 'react-redux';
import numeral from 'numeral';

const StatusLabelComponent = (props) => {
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
      labelText = `Battery: ${numeral(props.batteryLevel).format('0.00')} V`;
    }
  }
  return (
    <Label bsStyle={labelStyle}>{labelText}</Label>
  );
};

StatusLabelComponent.propTypes = {
  connectionStatus: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  batteryLevel: PropTypes.number.isRequired,
  batterySafety: PropTypes.bool.isRequired,
};


const mapStateToProps = state => ({
  batteryLevel: state.peripherals.batteryLevel,
  batterySafety: state.peripherals.batterySafety,
});

const StatusLabel = connect(mapStateToProps)(StatusLabelComponent);

export default StatusLabel;
