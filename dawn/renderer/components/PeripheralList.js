import React from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';
import { connect } from 'react-redux';
import { Panel, Accordion, ListGroup } from 'react-bootstrap';
import { PeripheralTypes } from '../constants/Constants';
import Peripheral from './Peripheral';

const cleanerNames = {};
cleanerNames[PeripheralTypes.MOTOR_SCALAR] = 'Motors';
cleanerNames[PeripheralTypes.SENSOR_BOOLEAN] = 'Boolean Sensors';
cleanerNames[PeripheralTypes.SENSOR_SCALAR] = 'Numerical Sensors';
cleanerNames[PeripheralTypes.LimitSwitch] = 'Limit Switches';
cleanerNames[PeripheralTypes.LineFollower] = 'Line Followers';
cleanerNames[PeripheralTypes.Potentiometer] = 'Potentiometers';
cleanerNames[PeripheralTypes.Encoder] = 'Encoders';
cleanerNames[PeripheralTypes.MetalDetector] = 'Metal Detectors';
cleanerNames[PeripheralTypes.ServoControl] = 'Servo Controllers';
cleanerNames[PeripheralTypes.RFID] = 'RFID';
cleanerNames[PeripheralTypes.YogiBear] = 'Yogi Bear';

const filter = new Set([PeripheralTypes.TeamFlag]);

const handleAccordion = (array) => {
  const peripheralGroups = {};

  array.filter(p => !filter.has(p.device_type)).forEach((p) => {
    if (!(p.device_type in peripheralGroups)) {
      peripheralGroups[p.device_type] = [];
    }
    peripheralGroups[p.device_type].push(p);
  });
  return (
    _.map(Object.keys(peripheralGroups), groups => (
      <Accordion style={{ marginBottom: '2px' }} key={`${cleanerNames[groups] || 'Default'}-Accordion`}>
        <Panel header={cleanerNames[groups] || 'Generic'} key={`${cleanerNames[groups] || 'Default'}-Panel`}>
          {
            _.map(peripheralGroups[groups], peripheral => (
              <Peripheral
                key={String(peripheral.uid)}
                id={String(peripheral.uid)}
                device_name={peripheral.device_name}
                device_type={peripheral.device_type}
                param={peripheral.param_value}
              />
            ))
          }
        </Panel>
      </Accordion>
    ))
  );
};


const PeripheralListComponent = (props) => {
  let errorMsg = null;
  if (!props.connectionStatus) {
    errorMsg = 'You are currently disconnected from the robot.';
  } else if (!props.runtimeStatus) {
    errorMsg = 'There appears to be some sort of Runtime error. ' +
      'No data is being received.';
  }

  let panelBody = null;
  if (errorMsg) {
    panelBody = <p className="panelText">{errorMsg}</p>;
  } else {
    panelBody = handleAccordion(
      _.sortBy(_.toArray(props.peripherals.peripheralList), ['device_type', 'device_name']));
  }

  return (
    <Panel
      id="peripherals-panel"
      header="Peripherals"
      bsStyle="primary"
    >
      <ListGroup fill style={{ marginBottom: '5px' }}>
        {panelBody}
      </ListGroup>
    </Panel>
  );
};

PeripheralListComponent.propTypes = {
  connectionStatus: PropTypes.bool.isRequired,
  runtimeStatus: PropTypes.bool.isRequired,
  peripherals: PropTypes.object.isRequired,
};

const mapStateToProps = state => ({
  peripherals: state.peripherals,
});

const PeripheralList = connect(mapStateToProps)(PeripheralListComponent);

export default PeripheralList;
