import React from 'react';
import PropTypes from 'prop-types';
import { Label } from 'react-bootstrap';
import { connect } from 'react-redux';
import numeral from 'numeral';

const StatusLabelComponent = (props) => {
  let labelStyle = 'default';
  let labelText = 'Disconnected';
  let labelText2 = ' ';
  let teamIP = ' ';
  if (props.masterStatus) {
    teamIP = props.ipAddress.substring(props.ipAddress.length-2, props.ipAddress.length)
    if (parseInt(teamIP) === props.teamNumber) {

    }
  }
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
      {'  '}
      <Label asStyle={labelStyle}>{labelText2}</Label>>
    </div>
  );
};

StatusLabelComponent.propTypes = {
  connectionStatus: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  batteryLevel: PropTypes.number.isRequired,
  batterySafety: PropTypes.bool.isRequired,
  masterStatus: PropTypes.bool.isRequired,
  teamColor: PropTypes.string.isRequired,
  teamNumber: PropTypes.number.isRequired,
  ipAddress: PropTypes.string.isRequired,
};


const mapStateToProps = state => ({
  batteryLevel: state.peripherals.batteryLevel,
  batterySafety: state.peripherals.batterySafety,
  masterStatus: state.fieldStore.masterStatus,
  teamNumber: state.fieldStore.teamNumber,
  teamColor: state.fieldStore.teamColor,
  ipAddress: state.info.ipAddress,
});

const StatusLabel = connect(mapStateToProps)(StatusLabelComponent);

export default StatusLabel;
