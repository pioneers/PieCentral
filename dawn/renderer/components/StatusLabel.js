import React from 'react';
import PropTypes from 'prop-types';
import { Label } from 'react-bootstrap';
import { connect } from 'react-redux';
import numeral from 'numeral';
import

const StatusLabelComponent = (props) => {
  let labelStyle = 'default';
  let labelText = 'Disconnected';
  const j = 'test';
  const g = 'test2';
  console.log("props.master: " + props.master);
  if (props.connectionStatus) {
    if (!props.runtimeStatus) {
      labelStyle = 'danger';
      labelText = 'General Error';
    } else if (props.batterySafety) {
      labelStyle = 'danger';
      labelText = 'Unsafe Battery';
    } else {
      labelStyle = 'success';
      labelText = `Battery: ${numeral(props.batteryLevel).format('0.00')} V`;
    }
  }
  return (
    <div id="parent">
      <Label bsStyle={labelStyle}>{labelText}</Label>
      <Label asStyle={j}>{g}</Label>
    </div>
  );
};

StatusLabelComponent.propTypes = {
  connectionStatus: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  batteryLevel: PropTypes.number.isRequired,
  batterySafety: PropTypes.bool.isRequired,
  master: PropTypes.bool.isRequired
};


const mapStateToProps = state => ({
  batteryLevel: state.peripherals.batteryLevel,
  batterySafety: state.peripherals.batterySafety,
  master: state.peripheral.master
});

const StatusLabel = connect(mapStateToProps)(StatusLabelComponent);

export default StatusLabel;
