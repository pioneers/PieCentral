import React from 'react';
import PropTypes from 'prop-types';
import { Label } from 'react-bootstrap';
import { connect } from 'react-redux';
import numeral from 'numeral';

const StatusLabelComponent = (props) => {
  let labelStyle = 'default';
  let labelText = 'Disconnected';
  const masterRobotHeader = 'Master Robot: Team ';
  const teamIP = props.ipAddress.substring(props.ipAddress.length - 2, props.ipAddress.length);
  let masterRobotStyle = ' ';
  if (props.teamColor === 'blue') {
    masterRobotStyle = 'primary';
  } else if (props.teamColor === 'gold') {
    masterRobotStyle = 'warning';
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
      {' '}
      <Label bsStyle={masterRobotStyle !== ' ' ? masterRobotStyle : labelStyle}>
        {(parseInt(teamIP, 10) === props.teamNumber &&
          props.fieldControlStatus) ? masterRobotHeader + teamIP : null}
      </Label>
    </div>
  );
};

StatusLabelComponent.propTypes = {
  connectionStatus: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  batteryLevel: PropTypes.number.isRequired,
  batterySafety: PropTypes.bool.isRequired,
  teamColor: PropTypes.string.isRequired,
  teamNumber: PropTypes.number.isRequired,
  ipAddress: PropTypes.string.isRequired,
  fieldControlStatus: PropTypes.bool.isRequired,
};


const mapStateToProps = state => ({
  batteryLevel: state.peripherals.batteryLevel,
  batterySafety: state.peripherals.batterySafety,
  masterStatus: state.fieldStore.masterStatus,
  teamNumber: state.fieldStore.teamNumber,
  teamColor: state.fieldStore.teamColor,
  ipAddress: state.info.ipAddress,
  fieldControlStatus: state.fieldStore.fieldControl,
});

const StatusLabel = connect(mapStateToProps)(StatusLabelComponent);

export default StatusLabel;
