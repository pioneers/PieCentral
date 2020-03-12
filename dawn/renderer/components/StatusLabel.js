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
  const shouldDisplayMaster = teamNumber => parseInt(teamIP, 10) === teamNumber
                                            && props.fieldControlStatus;
  let masterRobot = null;
  let masterRobotStyle = ' ';
  if (shouldDisplayMaster(props.blueMaster)) {
    masterRobot = props.blueMaster;
    masterRobotStyle = 'primary';
  } else if (shouldDisplayMaster(props.goldMaster)) {
    masterRobot = props.goldMaster;
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
        {masterRobot !== null ? masterRobotHeader + masterRobot : null}
      </Label>
    </div>
  );
};

StatusLabelComponent.propTypes = {
  connectionStatus: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  batteryLevel: PropTypes.number.isRequired,
  batterySafety: PropTypes.bool.isRequired,
  blueMaster: PropTypes.number.isRequired,
  goldMaster: PropTypes.number.isRequired,
  ipAddress: PropTypes.string.isRequired,
  fieldControlStatus: PropTypes.bool.isRequired,
};


const mapStateToProps = state => ({
  batteryLevel: state.peripherals.batteryLevel,
  batterySafety: state.peripherals.batterySafety,
  masterStatus: state.fieldStore.masterStatus,
  blueMaster: state.fieldStore.blueMaster,
  goldMaster: state.fieldStore.goldMaster,
  ipAddress: state.info.ipAddress,
  fieldControlStatus: state.fieldStore.fieldControl,
});

const StatusLabel = connect(mapStateToProps)(StatusLabelComponent);

export default StatusLabel;
